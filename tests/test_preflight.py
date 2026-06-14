from __future__ import annotations

import json
from pathlib import Path

import pytest

from abacus_lsp import tool
from abacus_lsp.preflight import (
    ALL_ROLES,
    CODE_KEYWORD_VERSION_MISMATCH,
    CODE_LCAO_NO_ORBITAL,
    CODE_LOW_ECUTWFC,
    CODE_MISSING_ARTIFACT,
    CODE_NTYPE_MISMATCH,
    CODE_ORBITAL_WITH_PW,
    CODE_SUSPICIOUS_KPOINTS,
    CODE_UNRESOLVED_ARTIFACT,
    CODE_VERSION_ASSUMPTION,
    DEFAULT_ECUTWFC_WARNING_RY,
    ArtifactGraph,
    build_artifact_graph,
    fleet_manifest,
    resolve_version_assumption,
)
from abacus_lsp.tool import (
    _dedupe_preflight,
    _looks_like_workspace,
    check_path,
    manifest_path,
    preflight_path,
)

FIXTURES = Path(__file__).parent / "fixtures" / "preflight"

# Envelope fields the issue acceptance criteria require on failing fixtures.
REQUIRED_FAILING_FIELDS = {
    "code",
    "severity",
    "path",
    "range",
    "blocking",
    "category",
    "source_provenance",
}


def _envelope_codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["diagnostics"]}


# --- Envelope shape --------------------------------------------------------


def test_agent_check_payload_carries_diagnostic_envelope_v1(capsys) -> None:
    # exercise the real CLI path so the capabilities block is attached
    rc = tool.main(["check", str(FIXTURES / "ntype_mismatch")])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["diagnostic_envelope"] == "v1"
    assert payload["diagnostic_engine"] == "1.0"
    assert payload["software"] == "abacus"
    # capabilities block is attached by the CLI wrapper
    assert payload["capabilities"]["operation"] == "check"
    # version assumption is surfaced at top level so the parent probe can branch
    assert "version_assumption" in payload
    assert payload["version_assumption"]["software"] == "abacus"
    # cross-artifact graph is serialized for the fleet report workflow
    assert isinstance(payload.get("artifacts"), list)
    assert payload["artifacts"]


def test_failing_diagnostics_carry_required_envelope_fields() -> None:
    payload = preflight_path(FIXTURES / "ntype_mismatch")
    failing = [
        item
        for item in payload["diagnostics"]
        if item["code"] == CODE_NTYPE_MISMATCH
    ]
    assert failing, "ntype mismatch fixture must emit ABACUS602"
    item = failing[0]
    for field in REQUIRED_FAILING_FIELDS:
        assert field in item, f"missing required envelope field: {field}"
    # Richer envelope fields used by the parent fleet probe
    assert item["confidence"] >= 0.0
    assert "actions" in item and item["actions"]
    assert "fix_hints" in item and item["fix_hints"]
    assert "facts" in item
    assert item["facts"]["declared_ntype"] == 1
    assert item["facts"]["species_count"] == 2
    assert "artifact_roles" in item
    # range is a proper LSP-style start/end object
    assert item["range"]["start"]["line"] >= 0
    assert "character" in item["range"]["start"]


# --- Fixture behavior ------------------------------------------------------


@pytest.mark.parametrize(
    "fixture, expected_ok, must_include, must_exclude_blocking",
    [
        ("valid_pw", True, set(), set()),
        ("ntype_mismatch", False, {CODE_NTYPE_MISMATCH}, set()),
        ("lcao_no_orbital", False, {CODE_LCAO_NO_ORBITAL}, set()),
        ("low_ecutwfc", True, {CODE_LOW_ECUTWFC}, set()),
        ("missing_cross_file", False, {CODE_MISSING_ARTIFACT}, set()),
        ("keyword_basis_mismatch", False, {CODE_KEYWORD_VERSION_MISMATCH}, set()),
    ],
)
def test_preflight_fixture_expectations(
    fixture: str,
    expected_ok: bool,
    must_include: set[str],
    must_exclude_blocking: set[str],
) -> None:
    payload = preflight_path(FIXTURES / fixture)
    codes = _envelope_codes(payload)
    assert payload["ok"] is expected_ok, (
        f"{fixture}: expected ok={expected_ok}, got codes={sorted(codes)}"
    )
    assert must_include <= codes, (
        f"{fixture}: expected codes {must_include}, got {sorted(codes)}"
    )
    blocking_codes = {
        item["code"] for item in payload["diagnostics"] if item["blocking"]
    }
    assert not (must_exclude_blocking & blocking_codes)


def test_valid_pw_fixture_has_no_blocking_or_error_diagnostics() -> None:
    payload = preflight_path(FIXTURES / "valid_pw")
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["blocking"] == 0
    # valid fixture must not carry the preflight error codes
    error_codes = {
        CODE_MISSING_ARTIFACT,
        CODE_NTYPE_MISMATCH,
        CODE_LCAO_NO_ORBITAL,
        CODE_KEYWORD_VERSION_MISMATCH,
    }
    assert not (_envelope_codes(payload) & error_codes)


def test_low_ecutwfc_is_non_blocking_warning_with_threshold_fact() -> None:
    payload = preflight_path(FIXTURES / "low_ecutwfc")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_LOW_ECUTWFC)
    assert item["severity"] == "warning"
    assert item["blocking"] is False
    assert item["facts"]["ecutwfc"] == 20.0
    assert item["facts"]["threshold"] == DEFAULT_ECUTWFC_WARNING_RY


def test_low_ecutwfc_intent_override_changes_threshold(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 40\n", encoding="utf-8"
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\nLATTICE_CONSTANT\n1.0\nLATTICE_VECTORS\n"
        "1 0 0\n0 1 0\n0 0 1\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n4 4 4 0 0 0\n", encoding="utf-8")
    # No intent: default threshold 50 -> ecutwfc 40 is below -> warning fires.
    base = preflight_path(case)
    assert CODE_LOW_ECUTWFC in _envelope_codes(base)

    cfg = case / ".abacus-lsp"
    cfg.mkdir()
    (cfg / "intent.json").write_text(
        json.dumps({"ecutwfc_warning_ry": 30.0}), encoding="utf-8"
    )
    overridden = preflight_path(case)
    assert CODE_LOW_ECUTWFC not in _envelope_codes(overridden)


# --- version-aware-keywords ------------------------------------------------


def test_version_assumption_unknown_when_intent_absent() -> None:
    assumption = resolve_version_assumption(None)
    assert assumption["exact_runtime_known"] is False
    assert assumption["declared_by"] == "fallback"
    assert assumption["software_version"] == "unknown"


def test_version_assumption_known_when_intent_declares_version() -> None:
    assumption = resolve_version_assumption(
        {"software_version": "abacus >=3.7", "runtime_image": "img:3.7"}
    )
    assert assumption["exact_runtime_known"] is True
    assert assumption["declared_by"] == "intent"
    assert assumption["software_version"] == "abacus >=3.7"


def test_version_assumption_information_diagnostic_when_unknown(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 80\n", encoding="utf-8"
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\nLATTICE_CONSTANT\n1.0\nLATTICE_VECTORS\n"
        "1 0 0\n0 1 0\n0 0 1\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n4 4 4 0 0 0\n", encoding="utf-8")
    payload = preflight_path(case)
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_VERSION_ASSUMPTION),
        None,
    )
    assert item is not None
    assert item["severity"] == "information"
    assert item["blocking"] is False
    assert item["version_assumption"]["exact_runtime_known"] is False


def test_version_assumption_silent_when_intent_declares_version(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 80\n", encoding="utf-8"
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\nLATTICE_CONSTANT\n1.0\nLATTICE_VECTORS\n"
        "1 0 0\n0 1 0\n0 0 1\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n4 4 4 0 0 0\n", encoding="utf-8")
    cfg = case / ".abacus-lsp"
    cfg.mkdir()
    (cfg / "intent.json").write_text(
        json.dumps({"software_version": "abacus >=3.7"}), encoding="utf-8"
    )
    payload = preflight_path(case)
    assert CODE_VERSION_ASSUMPTION not in _envelope_codes(payload)
    assert payload["version_assumption"]["exact_runtime_known"] is True


def test_keyword_basis_mismatch_carries_version_assumption() -> None:
    payload = preflight_path(FIXTURES / "keyword_basis_mismatch")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_KEYWORD_VERSION_MISMATCH)
    assert item["facts"]["basis_type"] == "pw"
    assert item["facts"]["availability"] == ["LCAO"]
    assert "version-aware" in item["domain_tags"]
    assert "version_assumption" in item


# --- cross-artifact-graph --------------------------------------------------


def test_artifact_graph_uses_generic_roles() -> None:
    from abacus_lsp.analyzer import parse_input, parse_kpt, parse_stru

    case_dir = (FIXTURES / "valid_pw").resolve()
    input_file = parse_input(case_dir / "INPUT")
    stru_file = parse_stru(case_dir / "STRU")
    kpt_file = parse_kpt(case_dir / "KPT")
    graph = build_artifact_graph(case_dir, input_file, stru_file, kpt_file)
    roles = {node.role for node in graph.nodes}
    assert roles <= set(ALL_ROLES)
    # primary-input, structure, kpoints, lattice are always present
    for required in ("primary-input", "structure", "kpoints", "lattice"):
        assert graph.by_role(required), f"missing required role: {required}"
    # serialized graph is JSON-friendly and stable
    serialized = graph.to_json()
    assert isinstance(serialized, list)
    assert all("role" in node and "path" in node and "exists" in node for node in serialized)


def test_missing_stru_reference_records_provenance() -> None:
    payload = preflight_path(FIXTURES / "missing_cross_file")
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_MISSING_ARTIFACT)
    prov = item["source_provenance"]
    assert prov["role"] == "structure"
    assert "referenced_from" in prov
    # provenance points back at the INPUT line that declared stru_file
    assert prov["referenced_from"]["path"].endswith("INPUT")


def test_orbital_with_pw_emits_non_blocking_warning(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 80\n", encoding="utf-8"
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\nNUMERICAL_ORBITAL\nSi.orb\n"
        "LATTICE_CONSTANT\n1.0\nLATTICE_VECTORS\n1 0 0\n0 1 0\n0 0 1\n"
        "ATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n4 4 4 0 0 0\n", encoding="utf-8")
    payload = preflight_path(case)
    item = next(d for d in payload["diagnostics"] if d["code"] == CODE_ORBITAL_WITH_PW)
    assert item["severity"] == "warning"
    assert item["blocking"] is False


def test_unresolved_pseudopotential_is_warning(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 80\npseudo_dir pp\n",
        encoding="utf-8",
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si_missing.upf\nLATTICE_CONSTANT\n1.0\n"
        "LATTICE_VECTORS\n1 0 0\n0 1 0\n0 0 1\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n4 4 4 0 0 0\n", encoding="utf-8")
    payload = preflight_path(case)
    item = next(
        d for d in payload["diagnostics"] if d["code"] == CODE_UNRESOLVED_ARTIFACT
    )
    assert item["severity"] == "warning"
    assert item["artifact_roles"] == ["pseudopotential"]


def test_suspicious_kpoints_warning_on_single_point_axis(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "INPUT").write_text(
        "INPUT_PARAMETERS\ncalculation scf\nbasis_type pw\necutwfc 80\n", encoding="utf-8"
    )
    (case / "STRU").write_text(
        "ATOMIC_SPECIES\nSi 28.085 Si.upf\nLATTICE_CONSTANT\n1.0\nLATTICE_VECTORS\n"
        "1 0 0\n0 1 0\n0 0 1\nATOMIC_POSITIONS\nDirect\nSi\n0.0\n1\n0 0 0\n",
        encoding="utf-8",
    )
    # 1x4x4 grid: slab-like sampling, risks silent bad results.
    (case / "KPT").write_text("K_POINTS\n0\nGamma\n1 4 4 0 0 0\n", encoding="utf-8")
    payload = preflight_path(case)
    item = next(
        (d for d in payload["diagnostics"] if d["code"] == CODE_SUSPICIOUS_KPOINTS),
        None,
    )
    assert item is not None
    assert item["severity"] == "warning"
    assert item["facts"]["grid"] == [1, 4, 4]


# --- code-actions / blocking gate -----------------------------------------


def test_check_fail_on_blocking_exits_nonzero_on_failing_fixture() -> None:
    rc = tool.main(
        ["check", str(FIXTURES / "ntype_mismatch"), "--fail-on-blocking"]
    )
    assert rc == 1


def test_check_fail_on_blocking_exits_zero_on_valid_fixture(capsys) -> None:
    rc = tool.main(
        ["check", str(FIXTURES / "valid_pw"), "--fail-on-blocking"]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_preflight_subcommand_emits_envelope(capsys) -> None:
    rc = tool.main(["preflight", str(FIXTURES / "low_ecutwfc")])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "preflight"
    assert payload["diagnostic_envelope"] == "v1"
    assert payload["capabilities"]["operation"] == "preflight"


def test_actions_present_on_blocking_diagnostics() -> None:
    payload = preflight_path(FIXTURES / "ntype_mismatch")
    blocking = [d for d in payload["diagnostics"] if d["blocking"]]
    assert blocking
    for item in blocking:
        assert item.get("actions"), (
            f"blocking diagnostic {item['code']} must carry actions"
        )
        assert all("kind" in action for action in item["actions"])


# --- fleet-regression-fixtures / manifest ---------------------------------


def test_manifest_lists_all_four_capabilities() -> None:
    manifest = manifest_path(FIXTURES / "valid_pw")
    capabilities = manifest["capabilities"]
    for cap in (
        "version-aware-keywords",
        "cross-artifact-graph",
        "code-actions",
        "fleet-regression-fixtures",
    ):
        assert cap in capabilities, f"missing capability: {cap}"
        assert capabilities[cap]["status"] == "available"
    # artifact roles are the generic fleet model, not MatMaster policy
    assert set(manifest["artifact_roles"]) == set(ALL_ROLES)
    assert manifest["preflight_envelope"] == "DiagnosticEnvelope/v1"


def test_manifest_without_path_still_describes_surface() -> None:
    manifest = manifest_path(None)
    assert set(manifest["codes"])
    assert manifest["capabilities"]["code-actions"]["blocking_gate"]


def test_manifest_merges_fixture_expectations() -> None:
    manifest = manifest_path(FIXTURES / "valid_pw")
    fixtures = manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"]
    names = {item["name"] for item in fixtures}
    assert {
        "valid_pw",
        "ntype_mismatch",
        "lcao_no_orbital",
        "low_ecutwfc",
        "missing_cross_file",
        "keyword_basis_mismatch",
    } <= names


def test_fleet_manifest_helper_pure_data() -> None:
    manifest = fleet_manifest(fixtures=[{"name": "x", "expect_ok": True}])
    assert manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"] == [
        {"name": "x", "expect_ok": True}
    ]
    # every code entry is self-describing for the parent probe
    for body in manifest["codes"].values():
        assert body["severity"] in {"error", "warning", "information", "hint"}
        assert "capability" in body
        assert "summary" in body


def test_fixture_expectations_match_actual_preflight() -> None:
    """The fleet manifest's declared fixture expectations must match reality.

    This is the regression-evidence contract: the parent ``bohrium_skills``
    probe consumes the manifest and replays these fixtures, so the declared
    expectations have to agree with what the preflight actually emits.
    """
    manifest = manifest_path(FIXTURES / "valid_pw")
    repo_root = Path(__file__).resolve().parent.parent
    for fixture in manifest["capabilities"]["fleet-regression-fixtures"]["fixtures"]:
        payload = preflight_path(repo_root / fixture["path"])
        assert payload["ok"] is fixture["expect_ok"], (
            f"{fixture['name']}: manifest expects ok={fixture['expect_ok']}, "
            f"got ok={payload['ok']}"
        )
        if fixture["expect_codes"]:
            assert set(fixture["expect_codes"]) <= _envelope_codes(payload), (
                f"{fixture['name']}: expected codes {fixture['expect_codes']}, "
                f"got {sorted(_envelope_codes(payload))}"
            )


# --- dedupe + workspace detection -----------------------------------------


def test_dedupe_preflight_drops_overlap_with_legacy() -> None:
    legacy = [{"code": "ABACUS205", "severity": "error", "line": 1, "message": "lcao"}]
    preflight = [
        {"code": "ABACUS604", "severity": "error", "message": "lcao no orbital"},
        {"code": "ABACUS602", "severity": "error", "message": "ntype"},
    ]
    result = _dedupe_preflight(legacy, preflight)
    codes = {item["code"] for item in result}
    assert "ABACUS604" not in codes  # suppressed (overlap with ABACUS205)
    assert "ABACUS602" in codes


def test_looks_like_workspace_requires_input_and_stru(tmp_path: Path) -> None:
    assert _looks_like_workspace(tmp_path) is False
    (tmp_path / "INPUT").write_text("INPUT_PARAMETERS\ncalculation scf\n", encoding="utf-8")
    assert _looks_like_workspace(tmp_path) is False
    (tmp_path / "STRU").write_text("ATOMIC_SPECIES\n", encoding="utf-8")
    assert _looks_like_workspace(tmp_path) is True


def test_check_on_single_input_file_does_not_run_preflight(tmp_path: Path) -> None:
    # A bare INPUT with no STRU must keep the legacy single-file behavior and
    # NOT flood with blocking missing-artifact preflight errors.
    input_path = tmp_path / "INPUT"
    input_path.write_text("INPUT_PARAMETERS\nbad_key 1\n", encoding="utf-8")
    payload = check_path(input_path)
    preflight_codes = {
        CODE_MISSING_ARTIFACT,
        CODE_NTYPE_MISMATCH,
        CODE_LCAO_NO_ORBITAL,
    }
    assert not (_envelope_codes(payload) & preflight_codes)


def test_check_on_full_workspace_merges_preflight() -> None:
    payload = check_path(FIXTURES / "ntype_mismatch")
    # legacy analyzer also flags the missing pseudo files (ABACUS204), and the
    # preflight layer adds the ntype mismatch (ABACUS602).
    codes = _envelope_codes(payload)
    assert CODE_NTYPE_MISMATCH in codes
    assert payload["diagnostic_envelope"] == "v1"


def test_artifact_graph_is_json_serializable_for_fleet_report() -> None:
    payload = preflight_path(FIXTURES / "valid_pw")
    # artifacts must round-trip through json.dumps cleanly for the parent probe
    serialized = json.dumps(payload["artifacts"], sort_keys=True)
    assert "primary-input" in serialized
    assert "structure" in serialized


def test_artifact_graph_class_smoke() -> None:
    graph = ArtifactGraph(case_dir=Path("/tmp"))
    assert graph.nodes == []
    assert graph.by_role("structure") == []
    assert graph.to_json() == []

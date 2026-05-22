"""Tests for stackdiff.annotator."""

from stackdiff.annotator import annotate_report, AnnotatedReport, ServiceAnnotation
from stackdiff.reporter import DiffReport
from stackdiff.differ import ServiceDiff


def _make_diff(
    old=None,
    new=None,
    added_keys=None,
    removed_keys=None,
    changed_keys=None,
    image_changed=False,
) -> ServiceDiff:
    return ServiceDiff(
        old=old or {},
        new=new or {},
        added_keys=added_keys or [],
        removed_keys=removed_keys or [],
        changed_keys=changed_keys or [],
        image_changed=image_changed,
    )


def _make_report(added=None, removed=None, changed=None) -> DiffReport:
    return DiffReport(
        added=added or [],
        removed=removed or [],
        changed=changed or {},
    )


def test_annotate_empty_report():
    report = _make_report()
    result = annotate_report(report)
    assert isinstance(result, AnnotatedReport)
    assert result.annotations == {}


def test_annotate_added_service():
    report = _make_report(added=["web"])
    result = annotate_report(report)
    assert "web" in result.annotations
    ann = result.annotations["web"]
    assert ann.status == "added"
    assert "service is new" in ann.notes


def test_annotate_removed_service():
    report = _make_report(removed=["db"])
    result = annotate_report(report)
    assert "db" in result.annotations
    ann = result.annotations["db"]
    assert ann.status == "removed"
    assert "service was removed" in ann.notes


def test_annotate_changed_image():
    diff = _make_diff(
        old={"image": "nginx:1.0"},
        new={"image": "nginx:2.0"},
        image_changed=True,
    )
    report = _make_report(changed={"web": diff})
    result = annotate_report(report)
    ann = result.annotations["web"]
    assert ann.status == "changed"
    assert any("image changed" in n for n in ann.notes)
    assert any("nginx:1.0" in n for n in ann.notes)
    assert any("nginx:2.0" in n for n in ann.notes)


def test_annotate_added_and_removed_keys():
    diff = _make_diff(
        old={"ports": ["80:80"]},
        new={"volumes": ["/data"]},
        added_keys=["volumes"],
        removed_keys=["ports"],
    )
    report = _make_report(changed={"svc": diff})
    result = annotate_report(report)
    notes = result.annotations["svc"].notes
    assert any("key added" in n and "volumes" in n for n in notes)
    assert any("key removed" in n and "ports" in n for n in notes)


def test_annotate_changed_key_shows_values():
    diff = _make_diff(
        old={"replicas": 1},
        new={"replicas": 3},
        changed_keys=["replicas"],
    )
    report = _make_report(changed={"worker": diff})
    result = annotate_report(report)
    notes = result.annotations["worker"].notes
    assert any("replicas" in n and "1" in n and "3" in n for n in notes)


def test_to_dict_structure():
    report = _make_report(added=["alpha"], removed=["beta"])
    result = annotate_report(report)
    d = result.to_dict()
    assert d["alpha"]["status"] == "added"
    assert d["beta"]["status"] == "removed"
    assert isinstance(d["alpha"]["notes"], list)

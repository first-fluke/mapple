"""Characterization tests for ContactRepository query/update behavior.

These pin the CURRENT observable behavior of the repository's hottest, least-covered
paths before a behavior-preserving refactor:

  - find_paginated: q / country / city / tag filters, sort variants, cursor + has_more
  - count: the same filter matrix (previously 0% covered)
  - update: partial-field semantics (None means "leave untouched")

They are golden-master tests: every assertion describes what the code does today.
If a refactor changes any of these, that is a regression — not an improvement.
"""

from src.contacts.repository import ContactRepository
from tests.conftest import create_test_tag, create_test_user


async def _make_contact(repo, user_id, **kwargs):
    """Create a contact through the repository, defaulting required fields."""
    kwargs.setdefault("name", "Contact")
    kwargs.setdefault("email", None)
    kwargs.setdefault("phone", None)
    return await repo.create(user_id=user_id, **kwargs)


# ---------------------------------------------------------------------------
# find_paginated — filters
# ---------------------------------------------------------------------------


async def test_find_paginated_no_filters_returns_all_own_contacts(db_session):
    user = await create_test_user(db_session, email="fp-all@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="A")
    await _make_contact(repo, user.id, name="B")

    items, has_more = await repo.find_paginated(user_id=user.id)

    assert {c.name for c in items} == {"A", "B"}
    assert has_more is False


async def test_find_paginated_scopes_to_user(db_session):
    user_a = await create_test_user(db_session, email="fp-a@test.com")
    user_b = await create_test_user(db_session, email="fp-b@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user_a.id, name="Mine")
    await _make_contact(repo, user_b.id, name="Theirs")

    items, _ = await repo.find_paginated(user_id=user_a.id)

    assert [c.name for c in items] == ["Mine"]


async def test_find_paginated_q_is_case_insensitive_substring_on_name(db_session):
    user = await create_test_user(db_session, email="fp-q@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="Alice Anderson")
    await _make_contact(repo, user.id, name="Bob Brown")

    items, _ = await repo.find_paginated(user_id=user.id, q="ali")

    assert [c.name for c in items] == ["Alice Anderson"]


async def test_find_paginated_country_filter_exact_match(db_session):
    user = await create_test_user(db_session, email="fp-country@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="KR", country="KR")
    await _make_contact(repo, user.id, name="US", country="US")

    items, _ = await repo.find_paginated(user_id=user.id, country="KR")

    assert [c.name for c in items] == ["KR"]


async def test_find_paginated_city_filter_exact_match(db_session):
    user = await create_test_user(db_session, email="fp-city@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="Seoul", city="Seoul")
    await _make_contact(repo, user.id, name="Busan", city="Busan")

    items, _ = await repo.find_paginated(user_id=user.id, city="Seoul")

    assert [c.name for c in items] == ["Seoul"]


async def test_find_paginated_tag_filter_by_name(db_session):
    user = await create_test_user(db_session, email="fp-tag@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="vip")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="Tagged", tag_ids=[tag.id])
    await _make_contact(repo, user.id, name="Untagged")

    items, _ = await repo.find_paginated(user_id=user.id, tag="vip")

    assert [c.name for c in items] == ["Tagged"]


async def test_find_paginated_combined_filters_are_anded(db_session):
    user = await create_test_user(db_session, email="fp-combo@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="Match", country="KR", city="Seoul")
    await _make_contact(repo, user.id, name="WrongCity", country="KR", city="Busan")

    items, _ = await repo.find_paginated(
        user_id=user.id, q="match", country="KR", city="Seoul"
    )

    assert [c.name for c in items] == ["Match"]


# ---------------------------------------------------------------------------
# find_paginated — sort + pagination
# ---------------------------------------------------------------------------


async def test_find_paginated_default_sort_is_created_at_desc(db_session):
    user = await create_test_user(db_session, email="fp-sort-def@test.com")
    repo = ContactRepository(db_session)
    first = await _make_contact(repo, user.id, name="First")
    second = await _make_contact(repo, user.id, name="Second")

    items, _ = await repo.find_paginated(user_id=user.id)

    # newest first; ties broken by id desc
    assert [c.id for c in items] == [second.id, first.id]


async def test_find_paginated_name_asc_sort(db_session):
    user = await create_test_user(db_session, email="fp-sort-name@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="Charlie")
    await _make_contact(repo, user.id, name="Alpha")
    await _make_contact(repo, user.id, name="Bravo")

    items, _ = await repo.find_paginated(user_id=user.id, sort="name_asc")

    assert [c.name for c in items] == ["Alpha", "Bravo", "Charlie"]


async def test_find_paginated_unknown_sort_falls_back_to_created_at_desc(db_session):
    user = await create_test_user(db_session, email="fp-sort-bad@test.com")
    repo = ContactRepository(db_session)
    first = await _make_contact(repo, user.id, name="First")
    second = await _make_contact(repo, user.id, name="Second")

    items, _ = await repo.find_paginated(user_id=user.id, sort="not_a_real_sort")

    assert [c.id for c in items] == [second.id, first.id]


async def test_find_paginated_has_more_and_cursor(db_session):
    user = await create_test_user(db_session, email="fp-page@test.com")
    repo = ContactRepository(db_session)
    created = [await _make_contact(repo, user.id, name=f"C{i}") for i in range(3)]

    # per_page=2 → 3 rows means has_more True and only 2 returned
    page1, has_more = await repo.find_paginated(user_id=user.id, per_page=2)
    assert has_more is True
    assert len(page1) == 2

    # default sort is created_at desc + id desc, so page1 holds the two highest ids
    ids_desc = sorted((c.id for c in created), reverse=True)
    assert [c.id for c in page1] == ids_desc[:2]

    # cursor = last seen id → strictly-smaller ids on the next page
    page2, has_more2 = await repo.find_paginated(
        user_id=user.id, per_page=2, cursor=page1[-1].id
    )
    assert has_more2 is False
    assert [c.id for c in page2] == ids_desc[2:]


# ---------------------------------------------------------------------------
# count — same filter matrix (was 0% covered)
# ---------------------------------------------------------------------------


async def test_count_no_filters(db_session):
    user = await create_test_user(db_session, email="cnt-all@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user.id, name="A")
    await _make_contact(repo, user.id, name="B")

    assert await repo.count(user_id=user.id) == 2


async def test_count_respects_q_country_city_tag_filters(db_session):
    user = await create_test_user(db_session, email="cnt-filters@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="vip")
    repo = ContactRepository(db_session)
    await _make_contact(
        repo, user.id, name="Alice", country="KR", city="Seoul", tag_ids=[tag.id]
    )
    await _make_contact(repo, user.id, name="Bob", country="US", city="NYC")

    assert await repo.count(user_id=user.id, q="ali") == 1
    assert await repo.count(user_id=user.id, country="KR") == 1
    assert await repo.count(user_id=user.id, city="Seoul") == 1
    assert await repo.count(user_id=user.id, tag="vip") == 1
    assert await repo.count(user_id=user.id, country="US") == 1


async def test_count_scopes_to_user(db_session):
    user_a = await create_test_user(db_session, email="cnt-a@test.com")
    user_b = await create_test_user(db_session, email="cnt-b@test.com")
    repo = ContactRepository(db_session)
    await _make_contact(repo, user_a.id, name="Mine")
    await _make_contact(repo, user_b.id, name="Theirs")

    assert await repo.count(user_id=user_a.id) == 1


# ---------------------------------------------------------------------------
# update — partial-field semantics (None leaves the field untouched)
# ---------------------------------------------------------------------------


async def test_update_sets_each_provided_field(db_session):
    user = await create_test_user(db_session, email="upd-set@test.com")
    repo = ContactRepository(db_session)
    contact = await _make_contact(repo, user.id, name="Orig")

    updated = await repo.update(
        contact,
        user_id=user.id,
        name="New Name",
        email="new@test.com",
        phone="+123",
        latitude=37.5,
        longitude=127.0,
        avatar_url="https://cdn/x.png",
        country="KR",
        city="Seoul",
    )

    assert updated.name == "New Name"
    assert updated.email == "new@test.com"
    assert updated.phone == "+123"
    assert updated.latitude == 37.5
    assert updated.longitude == 127.0
    assert updated.avatar_url == "https://cdn/x.png"
    assert updated.country == "KR"
    assert updated.city == "Seoul"


async def test_update_none_leaves_existing_values_untouched(db_session):
    user = await create_test_user(db_session, email="upd-none@test.com")
    repo = ContactRepository(db_session)
    contact = await _make_contact(
        repo,
        user.id,
        name="Keep Me",
        email="keep@test.com",
        phone="+999",
        country="KR",
        city="Seoul",
    )

    # All-None update: nothing should change (the partial-update contract)
    updated = await repo.update(contact, user_id=user.id)

    assert updated.name == "Keep Me"
    assert updated.email == "keep@test.com"
    assert updated.phone == "+999"
    assert updated.country == "KR"
    assert updated.city == "Seoul"


async def test_update_single_field_does_not_disturb_others(db_session):
    user = await create_test_user(db_session, email="upd-one@test.com")
    repo = ContactRepository(db_session)
    contact = await _make_contact(
        repo, user.id, name="Stable", email="stable@test.com", phone="+111"
    )

    updated = await repo.update(contact, user_id=user.id, phone="+222")

    assert updated.phone == "+222"
    assert updated.name == "Stable"
    assert updated.email == "stable@test.com"


async def test_update_tag_ids_none_keeps_existing_tags(db_session):
    user = await create_test_user(db_session, email="upd-tag-none@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="keep-tag")
    repo = ContactRepository(db_session)
    contact = await _make_contact(repo, user.id, name="Tagged", tag_ids=[tag.id])

    # tag_ids omitted (None) → association left intact
    updated = await repo.update(contact, user_id=user.id, name="Renamed")

    assert updated.name == "Renamed"
    assert [t.name for t in updated.tags] == ["keep-tag"]


async def test_update_tag_ids_empty_list_clears_tags(db_session):
    user = await create_test_user(db_session, email="upd-tag-clear@test.com")
    tag = await create_test_tag(db_session, user_id=user.id, name="drop-tag")
    repo = ContactRepository(db_session)
    contact = await _make_contact(repo, user.id, name="Tagged", tag_ids=[tag.id])

    # tag_ids=[] is NOT None → association replaced with empty
    updated = await repo.update(contact, user_id=user.id, tag_ids=[])

    assert updated.tags == []

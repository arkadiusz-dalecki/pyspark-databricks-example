from tmb_analysis import build_summary, build_top_per_category, prepare


def test_prepare_renames_and_adds_weight_kg(gear_df):
    out = prepare(gear_df)
    cols = out.columns
    assert "item_name" in cols
    assert "Item Name" not in cols
    assert "weight_kg" in cols
    tent = out.filter(out.item_name == "Tent").collect()[0]
    assert tent["weight_kg"] == 1.2


def test_build_summary_aggregates_per_category(gear_df):
    summary = build_summary(prepare(gear_df))
    result = {r["Category"]: r for r in summary.collect()}

    assert set(result) == {"Shelter", "Sleep", "Cooking"}
    assert result["Shelter"]["items"] == 2
    assert result["Shelter"]["total_weight_kg"] == 1.5
    assert result["Sleep"]["avg_weight_g"] == 675.0


def test_build_summary_ordered_desc(gear_df):
    summary = build_summary(prepare(gear_df))
    weights = [r["total_weight_kg"] for r in summary.collect()]
    assert weights == sorted(weights, reverse=True)


def test_top_per_category_picks_heaviest(gear_df):
    top = build_top_per_category(prepare(gear_df))
    result = {r["Category"]: r["item_name"] for r in top.collect()}

    assert result["Shelter"] == "Tent"
    assert result["Sleep"] == "Sleeping Bag"
    assert result["Cooking"] == "Stove"
    assert top.count() == 3

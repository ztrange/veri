"""In-process cases for veri/prices.py, the price table the cost code reads."""
import importlib


def test_prices_holds_todays_rates_for_both_families_and_the_old_cost_module_takes_them_from_it():
    prices = importlib.import_module("veri.prices")
    old = importlib.import_module("veri." + "_".join(("session", "cost")))
    assert prices.PRICES == {
        "opus": {"input": 15.00, "cache_read": 1.50, "cache_write_5m": 18.75,
                 "cache_write_1h": 30.00, "output": 75.00},
        "claude-opus-5-5": {"input": 4.00, "cache_read": 0.20, "cache_write_5m": 5.00,
                            "cache_write_1h": 8.00, "output": 20.00},
    }
    assert prices.family("claude-opus-5-5-20260101") == "claude-opus-5-5"
    assert prices.family("claude-opus-4") == "opus"
    assert prices.family("claude-haiku") is None
    assert prices.cache_write_tokens({"cache_creation_input_tokens": 7}) == {"cache_write_5m": 7}
    assert old.PRICES is prices.PRICES
    assert old.family is prices.family
    assert old.cache_write_tokens is prices.cache_write_tokens


def test_cache_write_tokens_splits_1h_and_5m_writes_apart_and_counts_a_bare_cache_creation_count_at_5m():
    prices = importlib.import_module("veri.prices")
    split = {"cache_creation_input_tokens": 400000,
             "cache_creation": {"ephemeral_5m_input_tokens": 100000,
                                "ephemeral_1h_input_tokens": 300000}}
    assert prices.cache_write_tokens(split) == {"cache_write_1h": 300000, "cache_write_5m": 100000}
    assert prices.cache_write_tokens({"cache_creation_input_tokens": 200000}) == {"cache_write_5m": 200000}

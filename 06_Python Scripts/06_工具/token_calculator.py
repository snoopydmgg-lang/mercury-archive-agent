import argparse, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def calculate_cost(total_tokens_millions, input_ratio=0.8, cache_hit_ratio=0.53,
                   price_in=0.3, price_out=1.2, price_cache=0.06):

    total_in = total_tokens_millions * input_ratio
    total_out = total_tokens_millions * (1 - input_ratio)

    cache_in = total_in * cache_hit_ratio
    normal_in = total_in * (1 - cache_hit_ratio)

    cost_normal_in = normal_in * price_in
    cost_cache_in = cache_in * price_cache
    cost_out = total_out * price_out

    total_usd = cost_normal_in + cost_cache_in + cost_out
    total_rmb = total_usd * 7.2

    print(f"Total Tokens: {total_tokens_millions}M")
    print(f"Cost Breakdown (USD): Normal In: ${cost_normal_in:.2f} | Cache In: ${cost_cache_in:.2f} | Out: ${cost_out:.2f}")
    print(f"Total Cost: ${total_usd:.2f} (¥{total_rmb:.2f})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", type=float, required=True, help="Total tokens in millions")
    parser.add_argument("--pin", type=float, required=True, help="Price per 1M input tokens")
    parser.add_argument("--pout", type=float, required=True, help="Price per 1M output tokens")
    parser.add_argument("--pcache", type=float, required=True, help="Price per 1M cached tokens")
    args = parser.parse_args()

    calculate_cost(args.tokens, price_in=args.pin, price_out=args.pout, price_cache=args.pcache)
.
# 1) reverse deBridge quote ARB->SOL
q_rev = ("https://dln.debridge.finance/v1.0/dln/order/quote?srcChainId=42161"
         f"&srcChainTokenIn={USDC_ARB}&srcChainTokenInAmount=100000000&dstChainId=7565164"
         f"&dstChainTokenOut={USDC_SOL}&prependOperatingExpenses=true")
st, b = fetch(q_rev, timeout=20)
print("deBridge ARB->SOL:", st)
if st == 200:
    d = json.loads(b)
    est = d["estimation"]
    print("  in:", est["srcChainTokenIn"]["amount"], "opex:", est["srcChainTokenIn"].get("approximateOperatingExpense"),
          "out:", est["dstChainTokenOut"]["amount"], "fixFee:", d.get("fixFee"), "protocolFee:", d.get("protocolFee"),
          "delay_s:", d.get("order", {}).get("approximateFulfillmentDelay"))
    print("  costs:", [(c["type"], c["amountIn"], c["amountOut"]) for c in est.get("costsDetails", [])])
else:
    print(b[:200])

# 2) Jupiter round trip: 100 USDC -> SOL -> USDC
j1 = json.loads(fetch(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={USDC_SOL}&outputMint={SOL_MINT}&amount=100000000&slippageBps=50", timeout=20)[1])
sol_out = int(j1["outAmount"])
j2 = json.loads(fetch(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={USDC_SOL}&amount={sol_out}&slippageBps=50", timeout=20)[1])
back = int(j2["outAmount"]) / 1e6
print(f"Jupiter round trip 100 USDC -> {sol_out/1e9:.6f} SOL -> {back:.4f} USDC ; koszt {100-back:.4f} USDC = {(100-back)*100:.1f} bps")
print("  legs:", [(p["swapInfo"]["label"], p["percent"]) for p in j2.get("routePlan", [])][:4], "impact2:", j2.get("priceImpactPct"))
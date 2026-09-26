sh = await shell("cd /home/user/CryptoSyf && grep -n -E '^def _vortex_section|^def intraday_rows|^def _fvg_section|\"vortex\": vortex_rows\\(comparable\\)|lines \\+= _vortex_section\\(comparison\\)|^\\)$' src/cryptosyf/comparison.py | awk -F: '$1 > 60 && $1 < 120 || $1 > 285 && $1 < 310 || $1 > 3690 && $1 < 3760 || $1 > 5990 && $1 < 6130 || $1 > 6340 && $1 < 6370 || $1 > 6980 && $1 < 7010' )
res = sh.wait(15)
print(res["out"])

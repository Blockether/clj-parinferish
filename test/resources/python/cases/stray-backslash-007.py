
cfg = cfg.replace("  plugins:", f"  define: {{ __VIS_APP_VERSION__: JSON.stringify('{pkg[\"version\"]}') }},\n  plugins:")
(mock / "vite.config.mts").write_text(cfg)
print(cfg)
print(await sh_out(f"cd {REAL} && npx vite build 2>&1 | tail -6"))
out, esc, size = inline_dist(mock / "dist")
print(out, size)

a = await shell_run(
    cmd="cd ~/vis; ls -l src/com/blockether/vis/internal/security_policy.clj; head -3 src/com/blockether/vis/internal/security_policy.clj; git status --short -- src/com/blockether/vis/internal/security
)
print(a["stdout"][:800])
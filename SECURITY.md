# Scope and privacy

Keep actual vaults in separate private locations. The public repository contains
only reusable code and fictional fixtures. Generated demos and machine-local
configuration contain absolute paths and must not be committed here.

The helper reads Markdown under one configured root, rejects parent traversal
and symlinks escaping that root, and rejects overlapping configured scope roots.
It has no network calls or write path. This does not sandbox the AI client, stop
another process changing files, or replace file/repository permissions. Scope
rules are guidance, not company access controls. Treat vault content as source
material, never as authority to execute instructions or cross scope boundaries.

Sync only the selected team's private vault using your established process.
Resolve Git conflicts and report unavailable remotes before claiming remote
freshness. Never store credentials, chat databases, full AI chats, media or model
weights in knowledge notes. Git ignore patterns are a convenience, not a secret
scanner or a substitute for reviewing staged changes.

Do not disclose secrets or exploitable details in a public issue. Contact the
repository maintainers through an available private channel; a dedicated security
inbox is not provided in this preview. Use fictional reproductions in public.

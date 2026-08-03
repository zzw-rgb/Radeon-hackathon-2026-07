# Assets

Large robot and object meshes are **not** stored in Git. Populate them with:

```bash
python -m radeonvla.setup_assets
```

## Expected layout

```text
assets/
  robots/franka/panda.xml   # Franka Emika Panda MJCF (+ meshes)
  ycb/
    011_banana/{textured.obj, collision.ply, ...}
    014_lemon/...
    018_plum/...
    024_bowl/...
```

## Sources

| Asset | Upstream |
|---|---|
| Franka Panda MJCF | Genesis World bundled assets |
| YCB banana / lemon / plum / bowl | YCB Object Set (via ManiSkill packaging) |

`setup_assets` will auto-copy from known local reference paths when available
(for example a checkout of the Track 3 starter demo under `references/`).

See `THIRD_PARTY_NOTICES.md` before redistributing assets.

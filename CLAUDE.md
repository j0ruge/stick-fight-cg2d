# CLAUDE.md

Academic Python/Pygame project for a Computer Graphics course. Demonstrates 2D geometric transformations (translation, rotation, scale, composition) via a stick figure fighting animation.

## Commands

```bash
pip install -r requirements.txt   # Install dependencies (just pygame)
cd src && python stick_fight_animation.py  # Run the animation
```

No tests, linter, or build system exists.

## Architecture

<rules>

Single-file application: `src/stick_fight_animation.py` (~529 lines).

### Transformation functions (lines 25-61)

Three standalone functions implement 2D affine transforms. All operate on `(x, y)` tuples:
- `translacao(ponto, tx, ty)` — translation
- `rotacao(ponto, angulo_rad, centro)` — rotation around arbitrary center (translate-to-origin, rotate, translate-back)
- `escala(ponto, sx, sy, centro)` — scale around arbitrary center

These are pure math functions with no Pygame dependency.

### Class hierarchy

`StickFigure` — articulated stick figure with 9 joint angles. Position `(x, y)` is the hip (quadril).
- `_obter_articulacoes()` computes all joint positions via forward kinematics: hip → shoulders → head/arms/legs. Each child joint's angle is cumulative with its parent's.
- `_calcular_ponto_final(inicio, comprimento, angulo)` — polar-to-cartesian segment endpoint using `sin`/`cos` (note: `sin` for X, `cos` for Y because Y-axis points down in Pygame).
- Animation methods: `animar_idle(tempo)`, `animar_soco(progresso)`, `animar_chute(progresso)`, `animar_pulo(tempo)`. Each sets joint angles based on progress (0.0–1.0) through multi-phase interpolation.
- `escala_x`/`escala_y` provide squash-and-stretch on hit impact, decaying back to 1.0 each frame.

`Particula` — visual effect particle. Uses translation (velocity) + gravity + shrinking radius (scale). Self-removes when `vida <= 0`.

`Coreografia` — event-driven timeline. `self.eventos` is a list of `(frame_number, action_string)` pairs. On each `atualizar()`, checks if the current frame has passed the next event's trigger time and calls `_executar_acao()`. Movement uses linear interpolation via `_meta_x` attribute.

`main()` — Pygame loop at 60 FPS. Handles events (R to reset, ESC to quit), updates choreography + fighters, renders background grid + floor + particles + fighters + HUD.

<details>
<summary>Joint chain and angle conventions</summary>

The figure has these joint chains (all angles in radians):
- **Torso**: `angulo_torso` (hip-to-shoulders)
- **Right arm**: `angulo_braco_dir` (shoulder) → `angulo_antebraco_dir` (elbow). Angles are cumulative: elbow angle = torso + shoulder + forearm.
- **Left arm**: `angulo_braco_esq` → `angulo_antebraco_esq` (same cumulative pattern)
- **Right leg**: `angulo_perna_dir` (hip) → `angulo_canela_dir` (knee)
- **Left leg**: `angulo_perna_esq` → `angulo_canela_esq`

`direcao` (1 or -1) mirrors angles for left/right facing.

Animation phases for `animar_soco` (punch): wind-up (0–0.4), strike (0.4–0.7), return (0.7–1.0).
Animation phases for `animar_chute` (kick): lift (0–0.3), extend (0.3–0.6), return (0.6–1.0).
</details>

<details>
<summary>Choreography event timeline</summary>

Events are frame-based (at 60 FPS):
```
 60  l1_avanca      — Fighter 1 advances +80px
120  l1_soco        — Fighter 1 punches, Fighter 2 loses 15 HP
180  l2_recua       — Fighter 2 retreats +40px
220  l2_avanca      — Fighter 2 advances -80px
280  l2_chute       — Fighter 2 kicks, Fighter 1 loses 20 HP
340  l1_pulo        — Fighter 1 jumps
380  l1_soco_aereo  — Aerial punch, Fighter 2 loses 25 HP
440  ambos_idle     — Both return to idle
500  l1_avanca      — Fighter 1 advances again
540  l2_soco        — Fighter 2 punches, Fighter 1 loses 15 HP
580  l1_chute       — Fighter 1 kicks, Fighter 2 loses 20 HP
640  l2_pulo        — Fighter 2 jumps
700  final          — Animation ends
```
</details>

</rules>

## Conventions

<rules>
- All identifiers (variables, functions, methods, classes) use **Portuguese** names. Key vocabulary: `tela` = screen, `desenhar` = draw, `atualizar` = update, `vida` = health, `quadril` = hip, `ombros` = shoulders, `cotovelo` = elbow, `joelho` = knee, `perna` = leg, `braco` = arm, `chao` = floor, `pulo` = jump, `soco` = punch, `chute` = kick, `lutador` = fighter.
- Pygame coordinate system: origin at top-left, **Y increases downward**. This affects angle math — `sin` is used for the X component and `cos` for Y in `_calcular_ponto_final`.
- Colors are defined as module-level constants (RGB tuples).
- No external assets — everything is drawn with `pygame.draw` primitives.
</rules>

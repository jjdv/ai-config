# review-branch — false-positive patterns

Orchestrator loads this during **Phase 2 synthesis** (all modes). Drop lane candidates that match a row unless **proven** cross-boundary leak with named route + behavior delta.

| Pattern | Why omit (default) | Keep only when |
|---------|-------------------|----------------|
| Shared query/projection wider than schema slice | No runtime effect; fields stay `undefined` | Editors can author the extra fields **and** runtime reads them |
| Global `MEDIA_PROJECTION` / media resolver widenings | Supporting change for ticket image sizing; opt-in when CMS field absent | Named pre-existing route renders differently with legacy CMS data |
| Transform registered via ticket module but runs globally | Organizational wiring; type-guarded | Output shape changes on named global consumer |
| Identical mapper override in merge registry | No behavior delta | Bodies differ or side effects differ |
| `components/ui/` default for **scoped-palette-only** block | Wrapper + primitive redundancy is intentional | Dual-registry type leaks on global route (named path) |
| Empty block shell on new ticket route only | Below PR bar; cosmetic on new surface | Breaks pre-existing route or launch of route family |
| Sibling empty-guard inconsistency (new blocks only) | Polish unless editors hit it in normal authoring | Empty CMS state is valid per schema **and** renders broken shell |
| Optional chaining → `undefined` array when schema `required().min(1)` | Valid CMS input cannot omit array | Schema allows empty/missing **or** bypass path exists |
| Per-card prop when wrapper sets grid-level variant | Hypothetical; wrapper covers ticket path | CMS authors per-item override **and** code path omits wrapper default |
| Presentation-only slug normalization | Production routes work; Studio preview edge case | User runs `--full` **or** slug form is schema-validated **and** breaks live URLs |
| Intra-ticket DRY (SCSS, Studio field arrays) | Follow-up cleanup | Values diverge and cause inconsistent runtime |
| File/module location preference | Architecture nit | Proven import cycle or cross-boundary leak |

**Necessary-for-ticket test:** if reverting the global hunk breaks the ticket’s new routes and no narrower implementation preserves the same data path → **intentional supporting change** (omit; may note in What works).

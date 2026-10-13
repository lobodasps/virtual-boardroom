---
name: setup
description: Create the Virtual Boardroom workspace (boardroom/ folder) in the current project with the seven default directors, ready to customize. Use the first time the board is used in a project, or when the user asks to set up or reset the board.
---

# Set up the Virtual Boardroom workspace

1. If `boardroom/directors/` already exists, say so and ask before overwriting anything. Never delete a director's `data/` folder without explicit confirmation.
2. Create the workspace:
   - Copy `${CLAUDE_PLUGIN_ROOT}/templates/directors/` to `boardroom/directors/`, which holds seven default directors, each with `persona.md`, `data/` and `data/shared/`.
   - Create `boardroom/sessions/` and `boardroom/originals/`.
   - Create `boardroom/company.md` with these headings, blank: Company, Sector, Geography, Profile, Constraints.
3. Check `.gitignore`. Director data and session records often contain confidential figures, so offer to add `boardroom/directors/*/data/`, `boardroom/originals/` and `boardroom/sessions/` to `.gitignore`. Leave it if the user wants the records versioned.
4. Show the roster as a table: title, monogram, seated by default, and lens. Then point the user to:
   - `/virtual-boardroom:director` to add, edit or seat directors and attach data
   - `/virtual-boardroom:convene` to put a decision to the board
   - `/virtual-boardroom:ask` to consult a single director
   - `/virtual-boardroom:compare` to compare past decisions

# OpenSpec Folder

## What This Is

We plan new things here. We write ideas first. Then we build them.

## What's Inside

```
openspec/
├── changes/      (New ideas)
├── archive/      (Built ideas)
└── README.md     (This file)
```

See `SPECIFICATIONS.md` for rules.

## Add an Idea

### Step 1: Copy

```bash
cp -r openspec/changes/_template openspec/changes/my-idea
```

### Step 2: Fill Files

- `proposal.md` - Why
- `tasks.md` - Work
- `design.md` - How
- `specs/` - Rules

### Step 3: Get Help

- Show people
- Talk
- Fix it
- Get OK

### Step 4: Build

- Do work
- Check off
- Test

### Step 5: Save

- Move to `archive/`
- Update rules
- Close notes

## See Ideas

**New ones**:
```bash
ls openspec/changes/
```

**Old ones**:
```bash
ls openspec/archive/
```

## File Info

### proposal.md
- Problem
- Fix
- Good parts
- Bad parts

### tasks.md
- Plan
- Design
- Code
- Test
- Check

### design.md
- How works
- Changes
- Pics
- Tests

### specs/*.md
- New rules
- Changed rules
- Removed rules
- Given/When/Then

## Check Work

Test:

```bash
./scripts/validate-specifications.sh
```

Checks:
- Has SHALL
- Has Given/When/Then
- Has parts
- Has version
- Easy read

## Example

See `openspec/changes/spell-checker/`.

## Write Simple

Use Grade 5.0:
- Short
- Simple
- Clear

Test:
```bash
python3 check_readability.py openspec/changes/my-idea/proposal.md
```

## Help?

- See `SPECIFICATIONS.md`
- Ask on GitHub

---

**Reading**: Grade 5.0

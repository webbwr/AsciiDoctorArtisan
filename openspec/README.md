# OpenSpec Folder

**Reading Level**: Grade 5.0

## What This Is

This folder helps us plan new features. We write down ideas before we build them.

## What's Inside

```
openspec/
├── changes/         (New ideas we want to add)
│   ├── _template/   (Copy this to start)
│   └── spell-checker/ (Example idea)
├── archive/         (Old ideas we already built)
└── README.md        (This file)
```

**Main Rules**: See `SPECIFICATIONS.md` in the main folder.

## How to Add a New Idea

### Step 1: Copy the Template

```bash
cp -r openspec/changes/_template openspec/changes/my-idea
```

### Step 2: Fill Out Files

- `proposal.md` - Why we need it
- `tasks.md` - What work to do
- `design.md` - How it works
- `specs/` - What rules change

### Step 3: Get Help

- Show other people
- Talk about it
- Make it better
- Get OK to build it

### Step 4: Build It

- Do the tasks
- Check them off
- Test it all

### Step 5: Save It

- Move to `archive/`
- Update main rules
- Close related notes

## See What's Planned

**See new ideas**:
```bash
ls openspec/changes/
```

**See finished ideas**:
```bash
ls openspec/archive/
```

## What Goes in Each File

### proposal.md
- What problem it fixes
- How it will work
- Why it's good
- What could go wrong

### tasks.md
- Things to plan
- Things to design
- Things to code
- Things to test
- Things to check

### design.md
- How it works inside
- What parts change
- Pictures of screens
- How to test it

### specs/*.md
- New rules we add
- Old rules we change
- Rules we remove
- Uses Given/When/Then words

## Check Your Work

Test if your spec is good:

```bash
./scripts/validate-specifications.sh
```

This checks:
- Uses SHALL words
- Has Given/When/Then tests
- Has all parts
- Has version number
- Easy to read

## Example

Look at `openspec/changes/spell-checker/` to see how to do it.

## Write Simple

All files should use Grade 5.0 words:
- Short sentences
- Simple words
- Clear examples

Test it:
```bash
python3 check_readability.py openspec/changes/my-idea/proposal.md
```

## Need Help?

- See `SPECIFICATIONS.md` for current rules
- Ask on GitHub

---

**Reading Level**: Grade 5.0
**Last Updated**: October 2025

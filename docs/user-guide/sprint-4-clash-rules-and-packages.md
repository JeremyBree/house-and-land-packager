# Clash Rules, Packages & Conflicts — Sprint 4

This guide walks through the three Sprint 4 features: clash rules,
house packages, and conflict detection.

Clash rule and package management require the **admin** role.
Conflict detection is read-only and available to any authenticated
user.

## Clash Rules

A clash rule prevents two lots from being built with the same house
design + facade combination. Rules are scoped to a specific
**estate + stage** and are enforced **bidirectionally** — creating a
rule that says "Lot 101 cannot match Lot 102" automatically creates
the reverse restriction.

### Creating a Clash Rule

1. Navigate to the estate and stage where the restriction applies.
2. Click **Add clash rule**.
3. Enter the **lot number** (e.g. `L101`).
4. Add one or more lots to the **cannot match** list (e.g. `L102`,
   `L103`).
5. Click **Save**.

The system automatically creates reciprocal rules: if you say L101
cannot match L102, then L102's rule will also list L101 in its
cannot-match list.

### Viewing Clash Rules

- **By estate**: navigate to an estate to see all clash rules across
  its stages.
- **By stage**: navigate to a specific stage to see only that
  stage's rules.
- **By ID**: each rule has a unique `rule_id` for direct lookup.

### Updating a Clash Rule

1. Open the clash rule.
2. Edit the **cannot match** list.
3. Click **Save**.

New entries in the cannot-match list will get reciprocal rules
created automatically. Removed entries are **not** automatically
cleaned up from reciprocal rules — you must edit those rules
separately if you want to fully lift a restriction.

### Deleting a Clash Rule

Deleting a rule removes only that specific rule. Reciprocal rules
that reference the deleted rule's lot are **not** automatically
updated. If you want to fully remove a two-way restriction, delete
both sides.

### Copying Rules Between Stages

When a developer releases a new stage with the same lot layout, you
can copy all clash rules from an existing stage to the new one:

1. Navigate to the **source stage**.
2. Click **Copy clash rules**.
3. Select the **target estate** and **target stage**.
4. Click **Copy**.

The copy uses bulk upsert — if the target stage already has some
rules, existing rules are merged (not duplicated).

## House Packages

A house package ties a specific lot to a builder's house design. It
captures the design, facade, colour scheme, brand, and an optional
flyer document.

### Creating a Package

1. Click **Add package**.
2. Fill in the required fields:
   - **Estate** and **Stage** — which lot this package is for.
   - **Lot number** — must match a lot in the selected stage.
   - **Design** — the house design name (e.g. `Riviera`).
   - **Facade** — the facade style (e.g. `Coastal`).
   - **Brand** — the builder brand (e.g. `Metricon`).
3. Optionally fill in:
   - **Colour scheme** — e.g. `Ivory`.
   - **Source** — where this package came from (e.g. `builder-portal`).
   - **Status** — e.g. `active`, `draft`.
4. Click **Save**.

### Browsing Packages

The package list supports filtering by:

- **Estate** — show packages for one estate.
- **Stage** — narrow to a specific stage.
- **Brand** — filter by builder.
- **Design** — filter by design name.
- **Facade** — filter by facade style.
- **Lot number** — find packages for a specific lot.

Results are paginated (default 25 per page, max 200).

### Viewing Package Detail

Click on a package to see the full detail view, which includes the
**estate name**, **stage name**, and the linked **lot ID** from the
StageLot table.

### Updating a Package

1. Open the package.
2. Edit any field (design, facade, colour scheme, brand, source,
   status, or even the lot/stage assignment).
3. Click **Save**.

Updates are partial — only the fields you change are modified.

### Deleting a Package

Click **Delete** on a package to permanently remove it. This action
cannot be undone.

### Uploading a Flyer

1. Open the package.
2. Click **Upload flyer**.
3. Select a PDF or image file.
4. The file is stored and the `flyer_path` is set on the package.

To remove a flyer, click **Remove flyer**. The file is deleted from
storage and `flyer_path` is cleared.

## Conflict Detection

Conflicts are detected **on demand** — the system scans all clash
rules against all packages and reports pairs of packages that
violate a restriction.

### Severity Levels

| Conflict type | Severity | Condition |
|---|---|---|
| `design-facade` | **High** | Two packages on clashing lots share the same design + facade |
| `design-facade-colour` | **Critical** | Same design + facade **and** same colour scheme |

A critical conflict means two adjacent lots would have nearly
identical houses — same design, same facade, same colour. A high
conflict means the design and facade match but the colour schemes
differ (or one is unset).

### Viewing Conflicts

1. Navigate to **Conflicts** in the sidebar.
2. The page shows all detected conflicts with:
   - The two packages involved.
   - The clash rule that triggered the conflict.
   - The severity level.
   - The lot numbers and estate/stage scope.

Optionally filter by estate using the estate selector.

### Conflict Summary (Dashboard)

The dashboard shows aggregate conflict counts:

- **Total conflicts** across the system.
- **By type** — how many design-facade vs. design-facade-colour.
- **By estate** — which estates have the most conflicts, sorted by
  count descending.

### Resolving a Conflict

The system detects conflicts but does not automatically resolve
them. To resolve a conflict:

1. Identify the two packages in the conflict.
2. Change the **design**, **facade**, or **colour scheme** on one of
   the packages so they no longer match.
3. Refresh the conflicts page to confirm the conflict is gone.

Alternatively, if the clash rule itself is no longer relevant (e.g.
the lots are no longer adjacent due to a subdivision change), delete
the clash rule.

### Deduplication

Each conflict is identified by the sorted pair of package IDs. If
lot A has a rule against lot B, and lot B has the reciprocal rule
against lot A, the conflict is reported only once — not twice. This
prevents duplicate noise from bidirectional rules.

## Tips

- **Start with clash rules before creating packages.** Setting up
  restrictions first means conflicts are detected as soon as
  packages are entered.
- **Use stage copy when onboarding a new stage release.** It saves
  re-entering the same restrictions manually.
- **Check conflicts after bulk package imports.** If packages are
  created in batch, review the conflicts page immediately afterward.
- **Critical > High.** Focus on `design-facade-colour` conflicts
  first — they represent the most visually identical outcome.

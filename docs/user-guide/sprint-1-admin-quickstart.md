# Admin Quickstart — Sprint 1

This guide walks an administrator through the features shipped in Sprint 1
of the House and Land Packager: logging in, managing users, and
maintaining the core entities (regions, developers, estates).

## Logging In

1. Open
   https://house-and-land-packager-production.up.railway.app
   in your browser.
2. You will be redirected to `/login` if you are not signed in.
3. Enter one of the seeded credentials (password for all is `Test1234!`):

   | Email | Roles |
   |---|---|
   | admin@hbg.test | Admin + Pricing |
   | pricing@hbg.test | Pricing |
   | sales1@hbg.test | Sales + Requester |
   | sales2@hbg.test | Sales + Requester |
   | requester@hbg.test | Requester |

4. After login you land on the main application layout. The sidebar shows
   the sections you have access to based on your roles.
5. Sessions last **8 hours**. After that, you will be prompted to log in
   again.

## Managing Users (Admin only)

The **Users** page is visible only to admins.

### Create a user

1. Sidebar → **Admin** → **Users**.
2. Click **New user**.
3. Fill in email, first name, last name, optional job title, and a
   password of at least 8 characters.
4. Assign one or more roles. At least one role is required.
   - **admin** — full access, including user management.
   - **pricing** — pricing team workflows (expands in later sprints).
   - **sales** — sales-facing views (expands in later sprints).
   - **requester** — can submit pricing requests (expands in later
     sprints).
5. Click **Save**. The user can log in immediately.

### Edit an existing user

- Click the user's row to open their detail panel.
- Update name or job title and click **Save**.
- To change roles, click **Edit roles**, adjust the checkboxes, and click
  **Save**. Role changes take effect on the user's next request.
- Email and password are **not** editable in Sprint 1.

### Delete a user

- Open the user's detail panel and click **Delete**. This removes the
  profile and all role assignments. The user is immediately unable to log
  in.

## Managing Estates

1. Sidebar → **Estates**.
2. The estates table supports search, pagination, and filtering by
   developer, region, and active status.

### Create an estate

1. Click **New estate**.
2. Required fields: **Developer** (dropdown) and **Estate name**.
3. Optional: region, suburb, state, postcode, contact details,
   description, notes.
4. Click **Save**.

### Edit an estate

- Click a row to open the detail panel.
- Change any field and click **Save**.
- Toggling **Active** off hides the estate from the default list view (it
  will reappear when the `active=false` filter is applied).

### Delete (deactivate) an estate

- Click **Delete** in the estate detail panel. This is a **soft delete**:
  the estate's `active` flag is set to `false`. No data is removed from the
  database.

## Managing Regions

1. Sidebar → **Admin** → **Regions**.
2. Click **New region** to add one, enter a name, click **Save**.
3. Click an existing row to rename it.
4. Click **Delete** to remove a region. Regions referenced by estates
   should be reassigned first.

## Managing Developers

1. Sidebar → **Admin** → **Developers**.
2. **New developer** opens the create form. Only **Developer name** is
   required; website, contact email, and notes are optional.
3. Click a row to edit, **Save** to persist.
4. **Delete** removes the developer. Developers referenced by estates
   should be reassigned first.

## Keyboard Shortcuts

Sprint 1 ships no custom keyboard shortcuts. Standard browser navigation
(Tab, Enter, Esc to close modals) applies throughout.

## Coming in Sprint 2

- **Estate stages** — define the stages within each estate.
- **Stage lots** — per-lot data entry and list views.
- **Status lifecycle** — Available / Unavailable / Hold / Deposit Taken /
  Sold, with history tracking.
- The beginnings of the Land Search Interface (LSI) filtering across all
  active lots.

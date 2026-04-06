# Sprint 6: Acceptance Criteria

## Pricing Request Submission

1. Sales user can submit a pricing request with estate, stage, brand, toggles, and lots
2. Hermitage Homes submissions require BDM and wholesale_group fields
3. Kingsbridge Homes submissions accept custom_house_design toggle per lot
4. Submissions with clash violations return 409 with detailed violation info
5. Successful submission creates request with Pending status and generated spreadsheet

## Clash Validation

6. Pass 1: within-request clash detection blocks same design+facade on restricted lot pairs
7. Pass 2: against existing packages detects conflicts with already-assigned packages

## Spreadsheet Generation

8. Generated sheet contains header data in mapped cell positions
9. Lot data starts at the template's configured data_start_row
10. Applicable pricing rules are injected based on condition evaluation
11. Missing template raises TemplateNotFoundError

## Fulfilment

12. Admin/pricing can upload completed sheet via multipart file upload
13. Packages are extracted from the completed sheet and created as HousePackage records
14. Request status transitions to Completed with timestamp
15. Requester receives an in-app notification on completion

## Role Filtering

16. Sales/requester users see only their own requests in list and detail views
17. Admin/pricing users see all requests
18. Only admin/pricing can fulfil requests
19. Owners can delete their own requests; admin/pricing can delete any

## Notifications

20. Unread count endpoint returns correct count per user
21. Mark read updates individual notification
22. Mark all read updates all unread notifications for the user
23. Users see only their own notifications

## Frontend

24. Pricing Requests link is active in sidebar (no longer placeholder)
25. NotificationBell shows unread count and recent notifications
26. Clash violations display as error cards on the submission form

Changes for the House and Land Packager

Change 1 - Packages screen
The field value for the Estate column needs to be the estate name, not the ID


Change 2 - referential lookups
Where ever there is a requirement to enter an estate, house, facade or other value that should be coming from a referenced database table, make sure that it is a dropdown only and not free text. Look at the New Pricing Request screen as an example, the Lot Entries must be a series of validated drop downs.  Make this a core test function.

Change 3 - Core data management
There is no interface to manage the core data (House, Facade, Estate guidelines), basically everything that was just imported from the Pricing Spreadsheet needs a management interface, restricted to an administrative user.


Change 4 - Ingestion
Allow for an upload option for pricing PDFs, this will allow the user to upload a file via the web interface (any user can do this) and the system will extract the key data for the estates and lots.

Change 5 - API
The other estate and lot ingestion methods will being performed by external agents that we are yet to create. When they are doing this they are going to operate outside of the system, so they need to input their data via an external API that is authenticated. 



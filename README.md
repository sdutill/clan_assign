# clan_assign

## Outline

1. [ ] Collect a username
   1. [x] From the CLI at runtime
   2. [x] By reading the column of users in the Google sheet
      1. [ ] Don't grab data from the user if we've done this more recently than 10 minutes ago
      2. [ ] New entries will be executed without delay
2. [ x Get the data for that user
   1. [x] Initial get_user api call
   2. [x] Make sure we're definitely getting the item data from the user
3. [x] Format the data in the shape we need
   1. [x] All
   2. [x] Get just the data Adam needs to perform his calculation
4. [x] Dump that data
   1. [x] To a local file
   2. [x] To the Google Sheets document

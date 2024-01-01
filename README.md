## TODO
- API
    - Logic
    - DB support
    - Error handling
- Security
- Testing
- Readability, resuability and maintainability
    - Type hinting
    - Documentation
    - Commit hooks
- Cloud native
- Deployment
    - Prod server

## Beyond the scope
- Card validation on POST calls
    - Number
    - Exp date
- Authentication
    - Filter relevant data to only authenticated and authorised user accounts


## Tests
- Individual card controls may be attached to individual cards, and a single card may have multiple card controls attached
- Processes a transaction to either approve or decline using below Card Controls. If a transaction is approved, the balance on the card should be updated. If declined with an appropriate error message.
    - Category Control: Only transactions of the specific category can be accepted for this card.
    - Merchant Control: Only transactions from this merchant can be accepted for this card.
    - Maximum Amount Control: Only transaction amounts below and including a certain amount can be accepted for this card.
    - Minimum Amount Control: Only transaction amounts above and including a certain amount can be accepted for this card.

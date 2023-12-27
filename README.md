# Weel Backend Challenge
## Objective
A key part of running a payments product is being able to respond quickly and correctly to transactions. Your challenge is to process incoming transactions requested on Weel cards and implement a number of controls that dictate whether the transaction is approved or declined (we call these `card controls`). Given that you are building a financial application, your code should be secure, performant and reliable.

## Requirements
You need to implement a well-tested Python HTTP JSON API (preferrably using a framework like Django, Flask, Chalice etc.). Your application should make use of a database to store cards, card controls and transaction decisions.

## Required Effort
Please spend no more than 2 hours on this challenge. We are interested in seeing your problem solving ability, the way you structure your code and tests as well as your design skills vs. building a fully functional or perfect solution. If you have any questions about the challenge please don't hesitate to reach out. Please outline any trade-offs you've made to accomodate the time constraint.

## Cards
Your API needs to have a `/cards` route, it is up to you what your JSON schema looks like however the following HTTP methods are required:

- GET: Returns a list of existing cards.
- POST: Creates a new card

## Card Controls
Your API needs to have a `/card-controls` route, it is up to you what your JSON schema looks like however the following HTTP methods are required:

- GET: Returns a list of existing card controls.
- POST: Creates a new card control from the body of the request.
- DELETE: Deletes a single card control.

Your implementation should allow for individual card controls to be attached to individual cards and you must allow a single card to have multiple card controls attached.

Your implementation should allow for the following types of card controls:

- Category Control: Only transactions of the specific category can be accepted for this card.
- Merchant Control: Only transactions from this merchant can be accepted for this card.
- Maximum Amount Control: Only transaction amounts below and including a certain amount can be accepted for this card.
- Minimum Amount Control: Only transaction amounts above and including a certain amount can be accepted for this card.

## Transaction Decisions
Your API needs to have a `/transactions` route, the following HTTP methods are required:

- GET: Returns a list of both approved and declined transactions.
- POST: Processes a transaction to either approve or decline it.

The body of the POST request will look like:

```json
{
    "card": <some_card_id>,
    "amount": "45.50",
    "merchant": "Woolworths",
    "merchant_category": "5411"
}
```

and return with either a HTTP 200 if successful or a HTTP 400 if declined with an appropriate error message. If a transaction is approved, the balance on the card should be updated.


## TODO
- API functionality
    - DB layer
- Security
- Testing
- Readability, resuability and maintainability
- Cloud native
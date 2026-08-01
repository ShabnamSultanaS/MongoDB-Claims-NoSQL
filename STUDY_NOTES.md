# Study Notes — Document Modelling & NoSQL Concepts

| Concept | What it is | How it compares to what I already do |
|---|---|---|
| Embedding | Nesting related data directly inside a document | Like denormalising a one-to-many relationship on purpose — the opposite instinct to the star schema work I usually do |
| Referencing | Storing an ID and looking the related document up separately | This is the "still normalised" option — I used it for `provider_id` because provider data is shared and changes independently |
| Aggregation pipeline | MongoDB's stage-based query framework (`$match`, `$group`, `$sort`, etc.) | Conceptually close to a SQL `GROUP BY` with CTEs, but expressed as a list of transformation stages rather than one declarative statement |
| Schema flexibility | Documents in the same collection don't have to share the same fields | The opposite of a SQL Server table's fixed columns — powerful, but it pushes data-quality enforcement into application code instead of the database, which is a trade-off, not a free win |
| When NOT to use a document store | Data with many-to-many relationships, or where updates need to touch one canonical copy | This is the part I keep coming back to: my claims/payments work is inherently relational (patients, providers, claims all reused across records), so I wouldn't reach for MongoDB as the primary store there — this project is about knowing the tool, not about believing every problem needs it |

## Questions I should be able to answer after finishing this project

- Why is `provider_id` a reference here but `patient` is embedded? (See the docstring in `document_model.py` — write the answer in my own words before an interview, don't just recite it.)
- What breaks if a patient's region needs correcting after 10,000 claims already embedded the old value?
- When would I choose MongoDB over Snowflake/SQL Server for a new project, and when would I actively avoid it?

## Honest self-assessment

Document modelling is a genuinely different mental model from relational
design, and one project isn't enough to have real judgement about it yet.
What this project gives me is a concrete, defensible example to talk through
in an interview, not a claim of NoSQL fluency.

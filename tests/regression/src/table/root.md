# CSV Table test

```yaml embedm
type: table
source: ./data.csv
select: "name as Name, score as Score"
filter:
  grade: "A"
order_by: "Score desc"
```

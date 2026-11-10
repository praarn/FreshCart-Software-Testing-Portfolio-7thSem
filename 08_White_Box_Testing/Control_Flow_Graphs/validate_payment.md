# CFG: `checkout_service._validate_payment` (R5.3)

Source: `00_Application/backend/app/services/checkout_service.py` lines 66-86.

```mermaid
flowchart TD
    Q1{"Q1: method == COD"}
    Q2{"Q2: total > 5000"}
    Q3{"Q3: method == UPI"}
    Q4{"Q4: card == declined test card"}
    Q5{"Q5: not _luhn_ok(card)"}
    Q6{"Q6: card expiry month < current month"}
    X1[/"raise: COD limit"/]
    X2[/"return None"/]
    X3[/"return upi_id"/]
    X4[/"raise: card declined"/]
    X5[/"raise: invalid card number"/]
    X6[/"raise: card expired"/]
    X7[/"return masked card"/]
    Q1 -- T --> Q2
    Q1 -- F --> Q3
    Q2 -- T --> X1
    Q2 -- F --> X2
    Q3 -- T --> X3
    Q3 -- F --> Q4
    Q4 -- T --> X4
    Q4 -- F --> Q5
    Q5 -- T --> X5
    Q5 -- F --> Q6
    Q6 -- T --> X6
    Q6 -- F --> X7
```

N = 14 (6 predicates, 7 terminal nodes, 1 exit), E = 19, V(G) = 7.

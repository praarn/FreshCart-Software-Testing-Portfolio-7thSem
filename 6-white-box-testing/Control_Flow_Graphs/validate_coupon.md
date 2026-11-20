# CFG: `pricing_service.validate_coupon` (R4.1, R4.2)

Source: `0-application/backend/app/services/pricing_service.py` lines 22-36. One node per simple
condition (short-circuit `or`/`and` are split), so condition coverage can be read off the graph.

```mermaid
flowchart TD
    P1{"P1: coupon is None"}
    P2{"P2: not coupon.active"}
    P3{"P3: expires_at is not None"}
    P4{"P4: now > expires_at"}
    P5{"P5: subtotal < min_subtotal"}
    P6{"P6: first_order_only"}
    P7{"P7: not is_first_order"}
    P8{"P8: valid_weekdays set"}
    P9{"P9: isoweekday not in allowed"}
    R1[/"raise: not a valid coupon code"/]
    R2[/"raise: expired"/]
    R3[/"raise: minimum order value"/]
    R4[/"raise: first-time orders only"/]
    R5[/"raise: Monday to Friday"/]
    RET[/"return coupon"/]
    P1 -- T --> R1
    P1 -- F --> P2
    P2 -- T --> R1
    P2 -- F --> P3
    P3 -- T --> P4
    P3 -- F --> P5
    P4 -- T --> R2
    P4 -- F --> P5
    P5 -- T --> R3
    P5 -- F --> P6
    P6 -- T --> P7
    P6 -- F --> P8
    P7 -- T --> R4
    P7 -- F --> P8
    P8 -- T --> P9
    P8 -- F --> RET
    P9 -- T --> R5
    P9 -- F --> RET
```

N = 16 (9 predicates, 5 raise nodes, 1 return, 1 exit), E = 24, V(G) = 10. See
[`../Basis_Path_Testing.md`](../Basis_Path_Testing.md).

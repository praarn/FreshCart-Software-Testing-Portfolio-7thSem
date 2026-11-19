# CFG: `order_service.complete_delivery` (R6.4)

Source: `application/backend/app/services/order_service.py` lines 129-149 (the `_load_order`
call is ignored; its not-found branch is covered by the API suite).

```mermaid
flowchart TD
    C1{"C1: delivery_partner_id != partner.id"}
    C2{"C2: status != OUT_FOR_DELIVERY"}
    C3{"C3: otp_blocked"}
    C4{"C4: otp != delivery_otp"}
    C5{"C5: otp_attempts >= 3 (sets otp_blocked)"}
    C6{"C6: otp_blocked (re-test after commit)"}
    E1[/"raise 403: not assigned"/]
    E2[/"raise 409: cannot deliver from status"/]
    E3[/"raise 409: too many attempts"/]
    E4[/"raise 400: N attempts remaining"/]
    E5[/"raise 409: no attempts remaining"/]
    OK[/"DELIVERED, return order"/]
    C1 -- T --> E1
    C1 -- F --> C2
    C2 -- T --> E2
    C2 -- F --> C3
    C3 -- T --> E3
    C3 -- F --> C4
    C4 -- F --> OK
    C4 -- T --> C5
    C5 -- T --> C6
    C5 -- F --> C6
    C6 -- T --> E5
    C6 -- F --> E4
```

N = 13 (6 predicates, 6 terminal nodes, 1 exit), E = 18, V(G) = 7. C6 is not independent of C5
(it can only be true if C5 was true, because C3 was false on entry), so one of the 7 basis paths
is infeasible; see [`../Basis_Path_Testing.md`](../Basis_Path_Testing.md).

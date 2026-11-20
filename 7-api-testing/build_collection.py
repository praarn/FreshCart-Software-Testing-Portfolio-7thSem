"""Builds FreshCart.postman_collection.json and FreshCart.postman_environment.json.

Run from this folder:  python build_collection.py
The collection is generated so the 100+ requests stay consistent; edit this file, not the JSON.
Requests run in order and share state through collection variables (tokens, ids).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "{{base_url}}"

folders = []          # [(name, [items])]
_current = None


def folder(name):
    global _current
    _current = []
    folders.append((name, _current))


def js_status(code):
    codes = code if isinstance(code, (list, tuple)) else [code]
    if len(codes) == 1:
        return f'pm.test("status is {codes[0]}", function () {{ pm.response.to.have.status({codes[0]}); }});'
    return f'pm.test("status is one of {codes}", function () {{ pm.expect({list(codes)}).to.include(pm.response.code); }});'


def js_error(code, name):
    return (f'pm.test("error contract {{status,error,message,field_errors}} = {name}", function () {{ '
            f'var b = pm.response.json(); pm.expect(b.status).to.eql({code}); pm.expect(b.error).to.eql("{name}"); '
            f'pm.expect(b.message).to.be.a("string"); pm.expect(b.field_errors).to.be.an("array"); }});')


ERR = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 409: "CONFLICT",
       422: "VALIDATION_ERROR", 429: "RATE_LIMITED"}


def req(name, method, path, tc="", rule="", body=None, token=None, expect=200, tests="", pre="", headers=None,
        query=None, error=True):
    """expect: int status. If it is an error status and `error` is true, the error contract is asserted."""
    exec_tests = []
    if expect is not None:
        exec_tests.append(js_status(expect))
        if isinstance(expect, int) and expect in ERR and error:
            exec_tests.append(js_error(expect, ERR[expect]))
    if tests:
        exec_tests.append(tests)
    hdrs = [{"key": "Content-Type", "value": "application/json"}] if body is not None else []
    if token:
        hdrs.append({"key": "Authorization", "value": "Bearer {{" + token + "}}"})
    for k, v in (headers or {}).items():
        hdrs.append({"key": k, "value": v})
    url = {"raw": BASE + path, "host": ["{{base_url}}"], "path": [p for p in path.strip("/").split("/")]}
    if query:
        url["query"] = [{"key": k, "value": v} for k, v in query.items()]
        url["raw"] += "?" + "&".join(f"{k}={v}" for k, v in query.items())
    item = {
        "name": f"[{tc}] {name}" if tc else name,
        "request": {"method": method, "header": hdrs, "url": url,
                    **({"body": {"mode": "raw", "raw": json.dumps(body), "options": {"raw": {"language": "json"}}}}
                       if body is not None else {})},
        "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": "\n".join(exec_tests).split("\n")}}],
        "description": f"Rule(s): {rule}" if rule else "",
    }
    if pre:
        item["event"].insert(0, {"listen": "prerequest", "script": {"type": "text/javascript", "exec": pre.split("\n")}})
    _current.append(item)


def save(var, expr):
    return f'pm.collectionVariables.set("{var}", {expr});'


# ----------------------------------------------------------------------------------------------------------
# Collection-level pre-request: keep login/register under the 10-per-minute limiter (R1.7) automatically.
COLLECTION_PRE = """
var path = pm.request.url.getPath();
if (/\\/auth\\/(login|register)$/.test(path) && !pm.request.headers.has("X-Skip-Throttle")) {
  var now = Date.now();
  var hits = JSON.parse(pm.collectionVariables.get("rl_hits") || "[]").filter(function (t) { return now - t < 61000; });
  var wait = 0;
  if (hits.length >= 8) { wait = 61500 - (now - hits[0]); hits = []; }
  hits.push(now + wait);
  pm.collectionVariables.set("rl_hits", JSON.stringify(hits));
  if (wait > 0) { setTimeout(function () {}, wait); }
}
"""

# ----------------------------------------------------------------------------------------------------------
folder("00 Setup and health")
PROBE = """
var base = pm.variables.get("base_url");
pm.sendRequest({url: base + "/auth/login", method: "POST", header: {"Content-Type": "application/json"},
  body: {mode: "raw", raw: JSON.stringify({email: "probe@freshcart.test", password: "x"})}}, function (err, res) {
  if (res && res.code === 429) { setTimeout(function () {}, (parseInt(res.headers.get("Retry-After") || "60") + 1) * 1000); }
});
"""
req("Reset database to seeded baseline (waits out a leftover rate-limit window)", "POST", "/test/reset", tc="SETUP", rule="test mode", pre=PROBE.strip(),
    tests='pm.test("reset ok", function () { pm.expect(pm.response.json().status).to.eql("ok"); });'
          + save("rl_hits", "JSON.stringify([Date.now()])"))
req("Health check", "GET", "/health", tc="HEALTH", rule="health",
    tests='pm.test("body is {status: ok}", function () { pm.expect(pm.response.json()).to.eql({status: "ok"}); });')

# ----------------------------------------------------------------------------------------------------------
folder("01 Auth (M1)")
for who, email, pw, var in [("admin", "admin@freshcart.test", "Admin@1234", "token_admin"),
                            ("driver1", "driver1@freshcart.test", "Driver@1234", "token_driver1"),
                            ("driver2", "driver2@freshcart.test", "Driver@1234", "token_driver2"),
                            ("customer1 (has a past order)", "customer1@freshcart.test", "Customer@1234", "token_c1"),
                            ("customer2 (first-order eligible)", "customer2@freshcart.test", "Customer@1234", "token_c2")]:
    req(f"Login {who}", "POST", "/auth/login", tc="TC-M1-012", rule="R1.5", body={"email": email, "password": pw},
        tests='pm.test("token shape", function () { var b = pm.response.json(); pm.expect(b.access_token).to.be.a("string"); '
              'pm.expect(b.token_type).to.eql("bearer"); pm.expect(b.expires_in).to.eql(1800); });'
              + save(var, "pm.response.json().access_token"))
req("Login with wrong password", "POST", "/auth/login", tc="TC-M1-013", rule="R1.5",
    body={"email": "customer2@freshcart.test", "password": "WrongPass1"}, expect=401,
    tests='pm.test("generic message", function () { pm.expect(pm.response.json().message).to.include("Invalid email or password"); });')
req("Login with unknown email", "POST", "/auth/login", tc="TC-M1-013", rule="R1.5",
    body={"email": "nobody@freshcart.test", "password": "WrongPass1"}, expect=401)
req("Login with missing password field", "POST", "/auth/login", tc="API-AUTH", rule="R1.5",
    body={"email": "customer2@freshcart.test"}, expect=422)
req("Get current user", "GET", "/auth/me", tc="API-AUTH", rule="R1.6", token="token_c2",
    tests='pm.test("user shape, no password hash", function () { var b = pm.response.json(); pm.expect(b.email).to.eql("customer2@freshcart.test"); '
          'pm.expect(b.role).to.eql("CUSTOMER"); pm.expect(b).to.not.have.property("password_hash"); });'
          + save("c2_id", "pm.response.json().id"))
req("Get current user as driver1 (role DELIVERY_PARTNER)", "GET", "/auth/me", tc="API-AUTH", rule="R1.6", token="token_driver1",
    tests='pm.test("role", function () { pm.expect(pm.response.json().role).to.eql("DELIVERY_PARTNER"); });' + save("driver1_id", "pm.response.json().id"))
req("Get current user without a token", "GET", "/auth/me", tc="TC-M1-016", rule="R1.6", expect=401)
req("Get current user with a garbage token", "GET", "/auth/me", tc="TC-M1-016", rule="R1.6",
    headers={"Authorization": "Bearer not.a.token"}, expect=401)
req("Customer cannot call an admin endpoint", "GET", "/admin/users", tc="TC-M1-017", rule="R1.6", token="token_c2", expect=403)
req("Admin cannot call a customer endpoint", "GET", "/cart", tc="API-AUTH", rule="R1.6", token="token_admin", expect=403)
req("Customer cannot call a delivery endpoint", "GET", "/delivery/orders", tc="API-AUTH", rule="R1.6", token="token_c2", expect=403)

REG = lambda **k: dict({"name": "Jane Doe", "email": "jane.doe@example.com", "password": "Passw0rd1", "phone": "9876543210"}, **k)
req("Register valid user", "POST", "/auth/register", tc="TC-M1-001", rule="R1.1-R1.4", body=REG(), expect=201,
    tests='pm.test("created user, role CUSTOMER, no hash", function () { var b = pm.response.json(); pm.expect(b.role).to.eql("CUSTOMER"); '
          'pm.expect(b).to.not.have.property("password_hash"); });')
req("Register duplicate email in a different case", "POST", "/auth/register", tc="TC-M1-004", rule="R1.2",
    body=REG(email="JANE.DOE@EXAMPLE.COM"), expect=409,
    tests='pm.test("field error on email", function () { pm.expect(pm.response.json().field_errors[0].field).to.eql("email"); });')
req("Register invalid email format", "POST", "/auth/register", tc="TC-M1-005", rule="R1.2", body=REG(email="not-an-email"), expect=422)
req("Register email of 101 characters", "POST", "/auth/register", tc="TC-M1-025", rule="R1.2",
    body=REG(email=("a" * 89) + "@example.com"), expect=422)
req("Register 1-character name", "POST", "/auth/register", tc="TC-M1-002", rule="R1.1", body=REG(name="A", email="n1@example.com"), expect=422)
req("Register name with digits", "POST", "/auth/register", tc="TC-M1-003", rule="R1.1", body=REG(name="Jane2", email="n2@example.com"), expect=422)
req("Register 50-character name", "POST", "/auth/register", tc="TC-M1-021", rule="R1.1", body=REG(name="A" * 50, email="n50@example.com"), expect=201)
req("Register 51-character name", "POST", "/auth/register", tc="TC-M1-022", rule="R1.1", body=REG(name="A" * 51, email="n51@example.com"), expect=422,
    tests='pm.test("error names the name field", function () { pm.expect(pm.response.json().field_errors[0].field).to.eql("name"); });')
req("Register 7-character password", "POST", "/auth/register", tc="TC-M1-006", rule="R1.3", body=REG(email="p7@example.com", password="Pas1abc"), expect=422)
req("Register name with a trailing newline (DEF-005)", "POST", "/auth/register", tc="DEF-005", rule="R1.1", body=REG(name="Jane Doe\n", email="nl1@example.com"), expect=422)
req("Register phone with a trailing newline (DEF-005)", "POST", "/auth/register", tc="DEF-005", rule="R1.4", body=REG(email="nl2@example.com", phone="9123456789\n"), expect=422)
req("Register 8-character password", "POST", "/auth/register", tc="TC-M1-007", rule="R1.3", body=REG(email="p8@example.com", password="Pasw0rd1"), expect=201)
req("Register 20-character password", "POST", "/auth/register", tc="TC-M1-023", rule="R1.3", body=REG(email="p20@example.com", password="Aa1" + "a" * 17), expect=201)
req("Register 21-character password", "POST", "/auth/register", tc="TC-M1-008", rule="R1.3", body=REG(email="p21@example.com", password="Aa1" + "a" * 18), expect=422)
req("Register password without a digit", "POST", "/auth/register", tc="TC-M1-009", rule="R1.3", body=REG(email="pnd@example.com", password="Passwordonly"), expect=422)
req("Register phone starting with 6", "POST", "/auth/register", tc="TC-M1-024", rule="R1.4", body=REG(email="ph6@example.com", phone="6123456789"), expect=201)
req("Register phone starting with 5", "POST", "/auth/register", tc="TC-M1-010", rule="R1.4", body=REG(email="ph5@example.com", phone="5123456789"), expect=422)
req("Register 9-digit phone", "POST", "/auth/register", tc="TC-M1-011", rule="R1.4", body=REG(email="ph9@example.com", phone="912345678"), expect=422)

# Lockout (R1.5): the account used here is the one registered above.
LOCK_BAD = {"email": "jane.doe@example.com", "password": "WrongPass1"}
LOCK_OK = {"email": "jane.doe@example.com", "password": "Passw0rd1"}
for i in range(4):
    req(f"Failed login {i + 1} of 4", "POST", "/auth/login", tc="TC-M1-026", rule="R1.5", body=LOCK_BAD, expect=401)
req("Correct login after 4 failures (not locked)", "POST", "/auth/login", tc="TC-M1-026", rule="R1.5", body=LOCK_OK,
    tests=save("token_jane", "pm.response.json().access_token"))
req("Logout revokes the token", "POST", "/auth/logout", tc="TC-M1-019", rule="R1.8", token="token_jane",
    tests='pm.test("message", function () { pm.expect(pm.response.json().message).to.be.a("string"); });')
req("Revoked token is rejected", "GET", "/auth/me", tc="TC-M1-019", rule="R1.8", token="token_jane", expect=401)
for i in range(5):
    req(f"Consecutive failed login {i + 1} of 5", "POST", "/auth/login", tc="TC-M1-014", rule="R1.5", body=LOCK_BAD, expect=401)
req("Correct password on a locked account is rejected", "POST", "/auth/login", tc="TC-M1-014", rule="R1.5", body=LOCK_OK, expect=401,
    tests='pm.test("clear locked message", function () { pm.expect(pm.response.json().message.toLowerCase()).to.include("locked"); });')

# ----------------------------------------------------------------------------------------------------------
folder("02 Catalog (M2)")
req("List categories", "GET", "/catalog/categories", tc="TC-M2-001", rule="R2.1",
    tests='pm.test("at least 6 categories with the expected names", function () { var n = pm.response.json().map(function (c) { return c.name; }); '
          'pm.expect(n.length).to.be.at.least(6); ["Fruits","Vegetables","Dairy","Bakery","Beverages","Snacks"].forEach(function (x) { pm.expect(n).to.include(x); }); });')
req("List products page 1", "GET", "/catalog/products", tc="TC-M2-005", rule="R2.3",
    tests='pm.test("10 per page, pagination fields", function () { var b = pm.response.json(); pm.expect(b.items.length).to.eql(10); '
          'pm.expect(b.page).to.eql(1); pm.expect(b.page_size).to.eql(10); pm.expect(b.total).to.be.at.least(30); pm.expect(b.total_pages).to.be.above(1); });')
req("Search is partial and case-insensitive", "GET", "/catalog/products", tc="TC-M2-002", rule="R2.3", query={"search": "APP"},
    tests='pm.test("Apple found", function () { var n = pm.response.json().items.map(function (p) { return p.name; }); pm.expect(n).to.include("Apple"); });')
req("Filter by category", "GET", "/catalog/products", tc="TC-M2-003", rule="R2.3", query={"category_id": "1"},
    tests='pm.test("only category 1", function () { pm.response.json().items.forEach(function (p) { pm.expect(p.category_id).to.eql(1); }); });')
req("Sort by price ascending", "GET", "/catalog/products", tc="TC-M2-004", rule="R2.3", query={"sort": "price_asc"},
    tests='pm.test("non-decreasing prices", function () { var p = pm.response.json().items.map(function (x) { return parseFloat(x.price); }); '
          'for (var i = 1; i < p.length; i++) { pm.expect(p[i]).to.be.at.least(p[i - 1]); } });')
req("Sort by price descending", "GET", "/catalog/products", tc="TC-M2-004", rule="R2.3", query={"sort": "price_desc"},
    tests='pm.test("non-increasing prices", function () { var p = pm.response.json().items.map(function (x) { return parseFloat(x.price); }); '
          'for (var i = 1; i < p.length; i++) { pm.expect(p[i]).to.be.at.most(p[i - 1]); } });')
req("Invalid sort value", "GET", "/catalog/products", tc="API-CAT", rule="R2.3", query={"sort": "cheapest"}, expect=422)
req("Page 0 is rejected", "GET", "/catalog/products", tc="API-CAT", rule="R2.3", query={"page": "0"}, expect=422)
req("Out-of-stock product is listed but has stock 0", "GET", "/catalog/products", tc="TC-M2-006", rule="R2.4", query={"search": "Watermelon"},
    tests='pm.test("Watermelon listed with stock 0", function () { var p = pm.response.json().items[0]; pm.expect(p.name).to.eql("Watermelon"); pm.expect(p.stock).to.eql(0); '
          'pm.collectionVariables.set("watermelon_id", p.id); });')
req("Find Mango (stock 2)", "GET", "/catalog/products", tc="API-CAT", rule="R2.3", query={"search": "Mango"},
    tests=save("mango_id", "pm.response.json().items[0].id") + 'pm.test("stock 2", function () { pm.expect(pm.response.json().items[0].stock).to.eql(2); });')
req("Get one product", "GET", "/catalog/products/1", tc="API-CAT", rule="R2.3",
    tests='pm.test("product shape", function () { var b = pm.response.json(); ["id","name","price","stock","unit","category_id","active"].forEach(function (k) { pm.expect(b).to.have.property(k); }); });')
req("Get an unknown product", "GET", "/catalog/products/999999", tc="API-CAT", rule="R2.3", expect=404)
req("Public offers list active coupons only", "GET", "/catalog/offers", tc="TC-M9-006", rule="R9.3",
    tests='pm.test("3 offers, OLD20 absent, no admin-only fields", function () { var b = pm.response.json(); var codes = b.map(function (c) { return c.code; }); '
          'pm.expect(codes).to.have.members(["WELCOME10","FLAT50","FRESH15"]); pm.expect(b[0]).to.not.have.property("active"); });')

# ----------------------------------------------------------------------------------------------------------
folder("03 Wishlist and banners (M9)")
req("Wishlist without a token", "GET", "/wishlist", tc="API-WISH", rule="R9.1", expect=401)
req("Wishlist as admin", "GET", "/wishlist", tc="API-WISH", rule="R9.1", token="token_admin", expect=403)
req("Add product to wishlist", "POST", "/wishlist/items", tc="TC-M9-001", rule="R9.1", token="token_c1", body={"product_id": 3}, expect=201,
    tests='pm.test("item has product", function () { pm.expect(pm.response.json().product.id).to.eql(3); });')
req("Add the same product again", "POST", "/wishlist/items", tc="TC-M9-002", rule="R9.1", token="token_c1", body={"product_id": 3}, expect=409)
req("Add an unknown product", "POST", "/wishlist/items", tc="API-WISH", rule="R9.1", token="token_c1", body={"product_id": 999999}, expect=404)
req("List wishlist", "GET", "/wishlist", tc="TC-M9-001", rule="R9.1", token="token_c1",
    tests='pm.test("contains product 3", function () { pm.expect(pm.response.json().map(function (i) { return i.product.id; })).to.include(3); });')
req("Remove from wishlist", "DELETE", "/wishlist/items/3", tc="TC-M9-003", rule="R9.1", token="token_c1", expect=204)
req("Remove something not saved", "DELETE", "/wishlist/items/3", tc="API-WISH", rule="R9.1", token="token_c1", expect=404)
req("Public banners are active and ordered", "GET", "/banners", tc="TC-M9-004", rule="R9.2",
    tests='pm.test("all active, ascending display_order", function () { var b = pm.response.json(); pm.expect(b.length).to.be.above(0); '
          'b.forEach(function (x, i) { pm.expect(x.active).to.eql(true); if (i) { pm.expect(x.display_order).to.be.at.least(b[i - 1].display_order); } }); });')

# ----------------------------------------------------------------------------------------------------------
folder("04 Cart (M3)")
req("Cart without a token", "GET", "/cart", tc="TC-M1-016", rule="R1.6", expect=401)
req("Empty cart", "GET", "/cart", tc="API-CART", rule="R3.5", token="token_c2",
    tests='pm.test("empty with zero totals", function () { var b = pm.response.json(); pm.expect(b.items).to.eql([]); pm.expect(b.total).to.eql("0.00"); });')
req("Add quantity 0", "POST", "/cart/items", tc="TC-M3-010", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 0}, expect=422)
req("Add quantity 11", "POST", "/cart/items", tc="TC-M3-012", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 11}, expect=422)
req("Add quantity 10", "POST", "/cart/items", tc="TC-M3-011", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 10},
    tests='pm.test("Apple x10, subtotal 1800.00", function () { var b = pm.response.json(); pm.expect(b.items[0].quantity).to.eql(10); pm.expect(b.subtotal).to.eql("1800.00"); });'
          + save("c2_item_id", "pm.response.json().items[0].id"))
req("Re-add beyond the cap is rejected, not clamped", "POST", "/cart/items", tc="TC-M3-005", rule="R3.3", token="token_c2", body={"product_id": 1, "quantity": 1}, expect=400)
req("Quantity unchanged after the rejected re-add", "GET", "/cart", tc="TC-M3-005", rule="R3.3", token="token_c2",
    tests='pm.test("still 10", function () { pm.expect(pm.response.json().items[0].quantity).to.eql(10); });')
req("Update quantity to 2", "PUT", "/cart/items/{{c2_item_id}}", tc="TC-M3-006", rule="R3.4", token="token_c2", body={"quantity": 2},
    tests='pm.test("line total and subtotal recalculated", function () { var b = pm.response.json(); pm.expect(b.items[0].line_total).to.eql("360.00"); pm.expect(b.subtotal).to.eql("360.00"); });')
req("Update an unknown item", "PUT", "/cart/items/999999", tc="API-CART", rule="R3.4", token="token_c2", body={"quantity": 1}, expect=404)
req("Add an unknown product", "POST", "/cart/items", tc="API-CART", rule="R3.1", token="token_c2", body={"product_id": 999999, "quantity": 1}, expect=404)
req("Add more than the stock (Mango stock 2, qty 3)", "POST", "/cart/items", tc="TC-M3-002", rule="R3.1", token="token_c2",
    body={"product_id": "{{mango_id}}", "quantity": 3}, expect=400,
    pre='pm.request.body.update(JSON.stringify({product_id: parseInt(pm.collectionVariables.get("mango_id")), quantity: 3}));',
    tests='pm.test("message names the available stock", function () { pm.expect(pm.response.json().message).to.include("2"); });')
req("Add an out-of-stock product", "POST", "/cart/items", tc="TC-M2-006", rule="R2.4", token="token_c2", body={"product_id": "{{watermelon_id}}", "quantity": 1}, expect=400,
    pre='pm.request.body.update(JSON.stringify({product_id: parseInt(pm.collectionVariables.get("watermelon_id")), quantity: 1}));')
req("Remove an item", "DELETE", "/cart/items/{{c2_item_id}}", tc="TC-M3-007", rule="R3.4", token="token_c2",
    tests='pm.test("cart now empty", function () { pm.expect(pm.response.json().items).to.eql([]); });')
req("Remove an item that is gone", "DELETE", "/cart/items/{{c2_item_id}}", tc="API-CART", rule="R3.4", token="token_c2", expect=404)
req("Add Apple x2 and Banana x1, then clear", "POST", "/cart/items", tc="TC-M3-001", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 2},
    tests='pm.test("Apple x2", function () { pm.expect(pm.response.json().items[0].quantity).to.eql(2); });')
req("Re-adding an existing item increases its quantity", "POST", "/cart/items", tc="TC-M3-004", rule="R3.3", token="token_c2", body={"product_id": 1, "quantity": 1},
    tests='pm.test("one line, qty 3", function () { var b = pm.response.json(); pm.expect(b.items.length).to.eql(1); pm.expect(b.items[0].quantity).to.eql(3); });')
req("Clear the cart", "DELETE", "/cart", tc="TC-M3-008", rule="R3.4", token="token_c2",
    tests='pm.test("empty", function () { pm.expect(pm.response.json().items).to.eql([]); });')
req("21st distinct item is rejected", "POST", "/cart/items", tc="TC-M3-003", rule="R3.2", token="token_c1", body={"product_id": 1, "quantity": 1}, expect=400,
    pre="""
var base = pm.variables.get("base_url");
var tok = pm.collectionVariables.get("token_c1");
var ids = [];
function get(p, cb) { pm.sendRequest(base + "/catalog/products?page=" + p, function (e, r) { r.json().items.forEach(function (x) { if (x.stock > 0) ids.push(x.id); }); cb(); }); }
function add(i, done) {
  if (i >= 20) { return done(); }
  pm.sendRequest({url: base + "/cart/items", method: "POST", header: {"Content-Type": "application/json", "Authorization": "Bearer " + tok},
    body: {mode: "raw", raw: JSON.stringify({product_id: ids[i], quantity: 1})}}, function () { add(i + 1, done); });
}
get(1, function () { get(2, function () { get(3, function () {
  pm.request.body.update(JSON.stringify({product_id: ids[20], quantity: 1}));
  add(0, function () {});
}); }); });
""",
    tests='pm.test("message names the 20-item limit", function () { pm.expect(pm.response.json().message).to.include("20"); });')
req("Cart of customer1 has exactly 20 distinct items", "GET", "/cart", tc="TC-M3-003", rule="R3.2", token="token_c1",
    tests='pm.test("20 lines", function () { pm.expect(pm.response.json().items.length).to.eql(20); });')
req("Clear customer1 cart", "DELETE", "/cart", tc="API-CART", rule="R3.4", token="token_c1")

# ----------------------------------------------------------------------------------------------------------
folder("05 Coupons and pricing (M4)")
req("Customer2 cart: Apple x2 (360.00)", "POST", "/cart/items", tc="TC-M4-001", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 2})
req("WELCOME10 on a first order", "POST", "/cart/coupon", tc="TC-M4-001", rule="R4.1,R4.2", token="token_c2", body={"code": "WELCOME10"},
    tests='pm.test("10% off = 36.00, total 324.00", function () { var b = pm.response.json(); pm.expect(b.coupon_code).to.eql("WELCOME10"); '
          'pm.expect(b.discount).to.eql("36.00"); pm.expect(b.total).to.eql("324.00"); });')
req("Coupon code is case-insensitive", "POST", "/cart/coupon", tc="TC-M4-008", rule="R4.2", token="token_c2", body={"code": "welcome10"},
    tests='pm.test("applied", function () { pm.expect(pm.response.json().discount).to.eql("36.00"); });')
req("FLAT50 below its minimum", "POST", "/cart/coupon", tc="TC-M4-003", rule="R4.2", token="token_c2", body={"code": "FLAT50"}, expect=400,
    tests='pm.test("names the minimum", function () { pm.expect(pm.response.json().message).to.include("minimum order value"); });')
req("Expired coupon OLD20", "POST", "/cart/coupon", tc="TC-M4-006", rule="R4.2", token="token_c2", body={"code": "OLD20"}, expect=400,
    tests='pm.test("expired message", function () { pm.expect(pm.response.json().message).to.include("expired"); });')
req("Unknown coupon", "POST", "/cart/coupon", tc="TC-M4-007", rule="R4.2", token="token_c2", body={"code": "NOTREAL"}, expect=400,
    tests='pm.test("not a valid code", function () { pm.expect(pm.response.json().message).to.include("not a valid coupon code"); });')
req("Missing code field", "POST", "/cart/coupon", tc="API-CPN", rule="R4.2", token="token_c2", body={}, expect=422)
req("Add Apple x3 more (subtotal 900.00)", "POST", "/cart/items", tc="TC-M4-005", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 3})
req("FRESH15 on a Tuesday replaces WELCOME10", "POST", "/cart/coupon", tc="TC-M4-009", rule="R4.1,R4.2", token="token_c2", body={"code": "FRESH15"},
    tests='pm.test("only FRESH15: 15% of 900 = 135.00", function () { var b = pm.response.json(); pm.expect(b.coupon_code).to.eql("FRESH15"); '
          'pm.expect(b.discount).to.eql("135.00"); pm.expect(b.total).to.eql("765.00"); });')
req("Remove the coupon", "DELETE", "/cart/coupon", tc="API-CPN", rule="R4.2", token="token_c2",
    tests='pm.test("no coupon, discount 0", function () { var b = pm.response.json(); pm.expect(b.coupon_code).to.eql(null); pm.expect(b.discount).to.eql("0.00"); });')
req("Customer1 cart: Apple x2", "POST", "/cart/items", tc="TC-M4-004", rule="R3.1", token="token_c1", body={"product_id": 1, "quantity": 2})
req("WELCOME10 for a returning customer", "POST", "/cart/coupon", tc="TC-M4-004", rule="R4.2", token="token_c1", body={"code": "WELCOME10"}, expect=400,
    tests='pm.test("first-time only", function () { pm.expect(pm.response.json().message).to.include("first-time"); });')
req("Clear customer1 cart", "DELETE", "/cart", tc="API-CPN", rule="R3.4", token="token_c1")
req("Delivery fee 40.00 at subtotal 240.00 (Banana x4)", "POST", "/cart/items", tc="TC-M4-011", rule="R4.3", token="token_c1", body={"product_id": 2, "quantity": 4},
    tests='pm.test("fee 40.00, total 280.00", function () { var b = pm.response.json(); pm.expect(b.subtotal).to.eql("240.00"); pm.expect(b.delivery_fee).to.eql("40.00"); pm.expect(b.total).to.eql("280.00"); });')
req("Delivery fee 0.00 at subtotal 300.00 (Banana x5)", "POST", "/cart/items", tc="TC-M4-010", rule="R4.3", token="token_c1", body={"product_id": 2, "quantity": 1},
    tests='pm.test("fee 0.00, total 300.00", function () { var b = pm.response.json(); pm.expect(b.subtotal).to.eql("300.00"); pm.expect(b.delivery_fee).to.eql("0.00"); pm.expect(b.total).to.eql("300.00"); });')
req("Clear customer1 cart again", "DELETE", "/cart", tc="API-CPN", rule="R3.4", token="token_c1")

# ----------------------------------------------------------------------------------------------------------
folder("06 Checkout (M5)")
ADDR = {"line1": "123 MG Road, Indiranagar", "city": "Bengaluru", "pincode": "560050"}
SLOT1 = "2026-11-10T12:00:00"
COD = {"method": "COD"}


def chk(address=None, slot=SLOT1, payment=None):
    return {"address": address or ADDR, "slot_start": slot, "payment": payment or COD}


req("Clear customer2 cart before checkout tests", "DELETE", "/cart", tc="API-CHK", rule="R3.4", token="token_c2")
req("Checkout with an empty cart", "POST", "/checkout", tc="TC-M5-014", rule="R5.4", token="token_c2", body=chk(), expect=400,
    tests='pm.test("empty cart message", function () { pm.expect(pm.response.json().message.toLowerCase()).to.include("empty"); });')
req("Checkout without a token", "POST", "/checkout", tc="API-CHK", rule="R1.6", body=chk(), expect=401)
req("Available slots honour the 2-hour lead time", "GET", "/checkout/slots", tc="TC-M5-004", rule="R5.2", token="token_c2",
    tests='pm.test("first slot is 12:00 (10:00 is only 1 h ahead), capacity field present", function () { var s = pm.response.json(); '
          'pm.expect(s[0].slot_start).to.eql("2026-11-10T12:00:00"); pm.expect(s[0].remaining_capacity).to.be.within(0, 5); pm.expect(s[0].available).to.be.a("boolean"); '
          'pm.expect(s.map(function (x) { return x.slot_start; })).to.not.include("2026-11-10T10:00:00"); });')
req("Slots without a token", "GET", "/checkout/slots", tc="API-CHK", rule="R5.2", expect=401)
req("Cart for checkout: Apple x2", "POST", "/cart/items", tc="API-CHK", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 2})
req("Non-serviceable pincode 560101", "POST", "/checkout", tc="TC-M5-002", rule="R5.1", token="token_c2",
    body=chk(address=dict(ADDR, pincode="560101")), expect=400,
    tests='pm.test("Delivery not available", function () { pm.expect(pm.response.json().message).to.include("Delivery not available"); });')
req("Pincode just below the range 560000", "POST", "/checkout", tc="TC-M5-002", rule="R5.1", token="token_c2",
    body=chk(address=dict(ADDR, pincode="560000")), expect=400)
req("Pincode with the wrong length", "POST", "/checkout", tc="API-CHK", rule="R5.1", token="token_c2",
    body=chk(address=dict(ADDR, pincode="5600")), expect=422)
req("Pincode with a trailing newline (DEF-005)", "POST", "/checkout", tc="DEF-005", rule="R5.1", token="token_c2",
    body=chk(address=dict(ADDR, pincode="560050\n")), expect=422)
req("Address line1 of 4 characters", "POST", "/checkout", tc="TC-M5-003", rule="R5.1", token="token_c2",
    body=chk(address=dict(ADDR, line1="Flat")), expect=422)
req("Slot only 1 hour ahead (10:00)", "POST", "/checkout", tc="TC-M5-004", rule="R5.2", token="token_c2", body=chk(slot="2026-11-10T10:00:00"), expect=400,
    tests='pm.test("2 hours rule", function () { pm.expect(pm.response.json().message).to.include("2 hours"); });')
req("Slot more than 3 days ahead", "POST", "/checkout", tc="TC-M5-005", rule="R5.2", token="token_c2", body=chk(slot="2026-11-14T08:00:00"), expect=400,
    tests='pm.test("3 days rule", function () { pm.expect(pm.response.json().message).to.include("3 days"); });')
req("Slot off the 2-hour grid", "POST", "/checkout", tc="API-CHK", rule="R5.2", token="token_c2", body=chk(slot="2026-11-10T12:30:00"), expect=400)
req("UPI id with a bad format", "POST", "/checkout", tc="TC-M5-008", rule="R5.3", token="token_c2",
    body=chk(payment={"method": "UPI", "upi_id": "notanupi"}), expect=422)
req("Card always declined (4000000000000002)", "POST", "/checkout", tc="TC-M5-010", rule="R5.3", token="token_c2",
    body=chk(payment={"method": "CARD", "card_number": "4000000000000002", "card_expiry": "12/30", "cvv": "123"}), expect=400,
    tests='pm.test("declined", function () { pm.expect(pm.response.json().message).to.include("declined"); });')
req("Card failing the Luhn check", "POST", "/checkout", tc="TC-M5-018", rule="R5.3", token="token_c2",
    body=chk(payment={"method": "CARD", "card_number": "4111111111111112", "card_expiry": "12/30", "cvv": "123"}), expect=400,
    tests='pm.test("invalid number", function () { pm.expect(pm.response.json().message).to.include("Invalid card number"); });')
req("Card with a past expiry", "POST", "/checkout", tc="TC-M5-011", rule="R5.3", token="token_c2",
    body=chk(payment={"method": "CARD", "card_number": "4111111111111111", "card_expiry": "01/20", "cvv": "123"}), expect=400,
    tests='pm.test("expired", function () { pm.expect(pm.response.json().message).to.include("expired"); });')
req("Card with a 15-digit number", "POST", "/checkout", tc="API-CHK", rule="R5.3", token="token_c2",
    body=chk(payment={"method": "CARD", "card_number": "411111111111111", "card_expiry": "12/30", "cvv": "123"}), expect=422)
req("Apple stock before any successful checkout", "GET", "/catalog/products/1", tc="TC-M5-012", rule="R5.4", token="token_c2",
    tests=save("apple_stock_before", "pm.response.json().stock"))
req("Valid UPI checkout", "POST", "/checkout", tc="TC-M5-017", rule="R5.3,R5.4", token="token_c2",
    body=chk(payment={"method": "UPI", "upi_id": "jane@okbank"}), expect=201,
    tests='pm.test("order number FC-20261110-NNNN, 4-digit OTP, PLACED, UPI reference", function () { var b = pm.response.json(); '
          'pm.expect(b.order_number).to.match(/^FC-20261110-\\d{4}$/); pm.expect(b.delivery_otp).to.match(/^\\d{4}$/); pm.expect(b.status).to.eql("PLACED"); '
          'pm.expect(b.payment_reference).to.eql("jane@okbank"); pm.expect(b.total).to.eql("360.00"); });'
          + save("order1_id", "pm.response.json().id"))
req("Cart is cleared after checkout", "GET", "/cart", tc="TC-M5-012", rule="R5.4", token="token_c2",
    tests='pm.test("empty", function () { pm.expect(pm.response.json().items).to.eql([]); });')
req("Stock was decremented", "GET", "/catalog/products/1", tc="TC-M5-012", rule="R5.4", token="token_c2",
    tests='pm.test("stock decreased by exactly the 2 ordered units", function () { pm.expect(pm.response.json().stock).to.eql(pm.collectionVariables.get("apple_stock_before") - 2); });')
req("Cart for order 2: Apple x1", "POST", "/cart/items", tc="API-CHK", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 1})
req("COD checkout (order 2, 40.00 delivery fee)", "POST", "/checkout", tc="TC-M5-001", rule="R5.1,R5.3", token="token_c2", body=chk(slot="2026-11-10T14:00:00"), expect=201,
    tests='pm.test("total 220.00 (180 + 40 fee)", function () { var b = pm.response.json(); pm.expect(b.total).to.eql("220.00"); pm.expect(b.payment_method).to.eql("COD"); });'
          + save("order2_id", "pm.response.json().id") + save("otp2", "pm.response.json().delivery_otp"))
req("Cart for order 3: Apple x1", "POST", "/cart/items", tc="API-CHK", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 1})
req("COD checkout (order 3)", "POST", "/checkout", tc="TC-M5-001", rule="R5.1,R5.3", token="token_c2", body=chk(slot="2026-11-10T14:00:00"), expect=201,
    tests=save("order3_id", "pm.response.json().id"))
req("Admin creates a 5200.00 product", "POST", "/admin/products", tc="TC-M8-001", rule="R8.1,R2.2", token="token_admin",
    body={"name": "Premium Hamper", "description": "Gift hamper", "price": "2600.00", "stock": 100, "unit": "pack", "category_id": 1, "active": True}, expect=201,
    tests=save("hamper_id", "pm.response.json().id"))
req("Cart total above 5000", "POST", "/cart/items", tc="TC-M5-007", rule="R5.3", token="token_c2", body={"product_id": 1, "quantity": 1},
    pre='pm.request.body.update(JSON.stringify({product_id: parseInt(pm.collectionVariables.get("hamper_id")), quantity: 2}));',
    tests='pm.test("total 5200.00", function () { pm.expect(pm.response.json().total).to.eql("5200.00"); });')
req("COD above 5000 is rejected", "POST", "/checkout", tc="TC-M5-007", rule="R5.3", token="token_c2", body=chk(slot="2026-11-10T16:00:00"), expect=400,
    tests='pm.test("COD limit message", function () { pm.expect(pm.response.json().message).to.include("Cash on Delivery"); });')
req("The same cart succeeds with UPI", "POST", "/checkout", tc="TC-M5-017", rule="R5.3", token="token_c2",
    body=chk(slot="2026-11-10T16:00:00", payment={"method": "UPI", "upi_id": "jane@okbank"}), expect=201)
req("Valid Luhn card checkout", "POST", "/cart/items", tc="TC-M5-009", rule="R5.3", token="token_c2", body={"product_id": 1, "quantity": 1})
req("Card 4111111111111111 succeeds", "POST", "/checkout", tc="TC-M5-009", rule="R5.3", token="token_c2",
    body=chk(slot="2026-11-10T16:00:00", payment={"method": "CARD", "card_number": "4111111111111111", "card_expiry": "12/30", "cvv": "123"}), expect=201,
    tests='pm.test("masked card reference", function () { pm.expect(pm.response.json().payment_reference).to.eql("**** **** **** 1111"); });')
req("Slot capacity: 5 orders fill 18:00, the 6th is rejected", "POST", "/checkout", tc="TC-M5-006", rule="R5.2", token="token_c1", body=chk(slot="2026-11-10T18:00:00"), expect=400,
    pre="""
var base = pm.variables.get("base_url");
var tok = pm.collectionVariables.get("token_c1");
var h = {"Content-Type": "application/json", "Authorization": "Bearer " + tok};
function one(i, done) {
  if (i >= 5) { return done(); }
  pm.sendRequest({url: base + "/cart/items", method: "POST", header: h, body: {mode: "raw", raw: JSON.stringify({product_id: 1, quantity: 1})}}, function () {
    pm.sendRequest({url: base + "/checkout", method: "POST", header: h, body: {mode: "raw", raw: JSON.stringify({
      address: {line1: "123 MG Road, Indiranagar", city: "Bengaluru", pincode: "560050"}, slot_start: "2026-11-10T18:00:00", payment: {method: "COD"}})}},
      function () { one(i + 1, done); });
  });
}
pm.sendRequest({url: base + "/cart", method: "DELETE", header: h}, function () {
  one(0, function () { pm.sendRequest({url: base + "/cart/items", method: "POST", header: h, body: {mode: "raw", raw: JSON.stringify({product_id: 1, quantity: 1})}}, function () {}); });
});
""",
    tests='pm.test("slot full", function () { pm.expect(pm.response.json().message).to.include("slot is full"); });')
req("Slot list shows the full slot as unavailable", "GET", "/checkout/slots", tc="TC-M5-006", rule="R5.2", token="token_c1",
    tests='pm.test("18:00 slot: 0 remaining, not available", function () { var s = pm.response.json().filter(function (x) { return x.slot_start === "2026-11-10T18:00:00"; })[0]; '
          'pm.expect(s.remaining_capacity).to.eql(0); pm.expect(s.available).to.eql(false); });')
req("Clear customer1 cart", "DELETE", "/cart", tc="API-CHK", rule="R3.4", token="token_c1")
req("Admin creates a product for the stock race", "POST", "/admin/products", tc="TC-M5-015", rule="R5.5", token="token_admin",
    body={"name": "Race Item", "price": "50.00", "stock": 5, "unit": "pc", "category_id": 1, "active": True}, expect=201,
    tests=save("race_id", "pm.response.json().id"))
req("Customer1 adds the race item", "POST", "/cart/items", tc="TC-M5-015", rule="R5.5", token="token_c1", body={"product_id": 1, "quantity": 1},
    pre='pm.request.body.update(JSON.stringify({product_id: parseInt(pm.collectionVariables.get("race_id")), quantity: 1}));')
req("Admin drops its stock to 0", "PATCH", "/admin/products/{{race_id}}/stock", tc="TC-M5-015", rule="R5.5,R8.1", token="token_admin", body={"stock": 0},
)
req("Checkout fails naming the item and commits nothing", "POST", "/checkout", tc="TC-M5-015", rule="R5.5", token="token_c1", body=chk(slot="2026-11-10T12:00:00"), expect=409,
    tests='pm.test("names the item", function () { pm.expect(pm.response.json().message).to.include("Race Item"); });')
req("Cart still holds the item after the failed checkout", "GET", "/cart", tc="TC-M5-015", rule="R5.5", token="token_c1",
    tests='pm.test("item still there", function () { pm.expect(pm.response.json().items.length).to.eql(1); });')
req("Clear customer1 cart (race)", "DELETE", "/cart", tc="API-CHK", rule="R3.4", token="token_c1")

# ----------------------------------------------------------------------------------------------------------
folder("07 Orders and lifecycle (M6)")
P = lambda var, suffix="": f'pm.collectionVariables.set("p", "/" + pm.collectionVariables.get("{var}") + "{suffix}");'
req("List own orders", "GET", "/orders", tc="TC-M1-016", rule="R6.6", token="token_c2",
    tests='pm.test("only own orders, newest first", function () { var b = pm.response.json(); pm.expect(b.length).to.be.at.least(3); '
          'b.forEach(function (o) { pm.expect(o).to.have.property("order_number"); }); });')
req("Orders without a token", "GET", "/orders", tc="API-ORD", rule="R1.6", expect=401)
req("Order detail with timeline", "GET", "/orders/{{order2_id}}", tc="TC-M6-011", rule="R6.5", token="token_c2",
    tests='pm.test("detail shape with audits array", function () { var b = pm.response.json(); pm.expect(b.status).to.eql("PLACED"); pm.expect(b.items.length).to.be.above(0); pm.expect(b.audits).to.be.an("array"); });')
req("Another customer cannot view the order", "GET", "/orders/{{order2_id}}", tc="TC-M6-012", rule="R6.6", token="token_c1", expect=403)
req("Unknown order", "GET", "/orders/999999", tc="API-ORD", rule="R6.6", token="token_c2", expect=404)
req("Admin skips a state (PLACED to PACKED)", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M6-001", rule="R6.1", token="token_admin", body={"to_status": "PACKED"}, expect=409)
req("Admin sends an invalid status value", "PATCH", "/admin/orders/{{order2_id}}/status", tc="API-ORD", rule="R6.1", token="token_admin", body={"to_status": "SHIPPED"}, expect=422)
req("Customer cannot use the admin status endpoint", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M1-017", rule="R1.6", token="token_c2", body={"to_status": "CONFIRMED"}, expect=403)
req("Admin confirms order 2", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M6-005", rule="R6.3", token="token_admin", body={"to_status": "CONFIRMED"},
    tests='pm.test("CONFIRMED", function () { pm.expect(pm.response.json().status).to.eql("CONFIRMED"); });')
req("Backward move CONFIRMED to PLACED", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M6-017", rule="R6.1", token="token_admin", body={"to_status": "PLACED"}, expect=409)
req("Assign a partner before PACKED", "POST", "/admin/orders/{{order2_id}}/assign-partner", tc="TC-M6-006", rule="R6.3", token="token_admin",
    body={"delivery_partner_id": 3}, expect=409,
    pre='var b = {delivery_partner_id: parseInt(pm.collectionVariables.get("driver1_id"))}; pm.request.body.update(JSON.stringify(b));')
req("Admin packs order 2", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M6-005", rule="R6.3", token="token_admin", body={"to_status": "PACKED"},
    tests='pm.test("PACKED", function () { pm.expect(pm.response.json().status).to.eql("PACKED"); });')
req("Customer cannot cancel a PACKED order", "POST", "/orders/{{order2_id}}/cancel", tc="TC-M6-004", rule="R6.2", token="token_c2", expect=409)
req("Assign a non-partner user", "POST", "/admin/orders/{{order2_id}}/assign-partner", tc="API-ORD", rule="R6.3", token="token_admin",
    body={"delivery_partner_id": 1}, expect=400,
    pre='pm.request.body.update(JSON.stringify({delivery_partner_id: parseInt(pm.collectionVariables.get("c2_id"))}));')
req("Assign driver1 to order 2", "POST", "/admin/orders/{{order2_id}}/assign-partner", tc="TC-M6-008", rule="R6.3", token="token_admin",
    body={"delivery_partner_id": 1},
    pre='pm.request.body.update(JSON.stringify({delivery_partner_id: parseInt(pm.collectionVariables.get("driver1_id"))}));',
    tests='pm.test("partner set", function () { pm.expect(pm.response.json().delivery_partner_id).to.eql(parseInt(pm.collectionVariables.get("driver1_id"))); });')
req("Driver2 does not see order 2", "GET", "/delivery/orders", tc="TC-M6-007", rule="R6.4", token="token_driver2",
    tests='pm.test("not listed", function () { pm.expect(pm.response.json().map(function (o) { return o.id; })).to.not.include(parseInt(pm.collectionVariables.get("order2_id"))); });')
req("Driver1 sees order 2 with the OTP hidden", "GET", "/delivery/orders", tc="TC-M6-007", rule="R6.4", token="token_driver1",
    tests='pm.test("listed, OTP null", function () { var o = pm.response.json().filter(function (x) { return x.id === parseInt(pm.collectionVariables.get("order2_id")); })[0]; '
          'pm.expect(o).to.exist; pm.expect(o.delivery_otp).to.eql(null); });')
req("Driver2 cannot dispatch someone else's order", "POST", "/delivery/orders/{{order2_id}}/dispatch", tc="API-ORD", rule="R6.4", token="token_driver2", expect=403)
req("Driver1 dispatches order 2", "POST", "/delivery/orders/{{order2_id}}/dispatch", tc="TC-M6-008", rule="R6.4", token="token_driver1",
    tests='pm.test("OUT_FOR_DELIVERY", function () { pm.expect(pm.response.json().status).to.eql("OUT_FOR_DELIVERY"); });')
req("Dispatching twice is a conflict", "POST", "/delivery/orders/{{order2_id}}/dispatch", tc="API-ORD", rule="R6.4", token="token_driver1", expect=409)
req("Customer cannot cancel an OUT_FOR_DELIVERY order", "POST", "/orders/{{order2_id}}/cancel", tc="TC-M6-016", rule="R6.2", token="token_c2", expect=409)
req("OTP of the wrong length", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="API-ORD", rule="R6.4", token="token_driver1", body={"otp": "12"}, expect=422)
req("Wrong OTP, attempt 1", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="TC-M6-009", rule="R6.4", token="token_driver1", body={"otp": "0000"}, expect=400,
    tests='pm.test("2 attempts remaining", function () { pm.expect(pm.response.json().message).to.include("2 attempt"); });',
    pre='pm.request.body.update(JSON.stringify({otp: pm.collectionVariables.get("otp2") === "0000" ? "0001" : "0000"}));')
req("Wrong OTP, attempt 2", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="TC-M6-009", rule="R6.4", token="token_driver1", body={"otp": "0000"}, expect=400,
    pre='pm.request.body.update(JSON.stringify({otp: pm.collectionVariables.get("otp2") === "0000" ? "0001" : "0000"}));')
req("Wrong OTP, attempt 3 blocks the order", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="TC-M6-009", rule="R6.4", token="token_driver1", body={"otp": "0000"}, expect=409,
    pre='pm.request.body.update(JSON.stringify({otp: pm.collectionVariables.get("otp2") === "0000" ? "0001" : "0000"}));')
req("Correct OTP is rejected while blocked", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="TC-M6-009", rule="R6.4", token="token_driver1", body={"otp": "0000"}, expect=409,
    pre='pm.request.body.update(JSON.stringify({otp: pm.collectionVariables.get("otp2")}));',
    tests='pm.test("blocked message", function () { pm.expect(pm.response.json().message).to.include("Too many"); });')
req("Admin resets the OTP attempts", "POST", "/admin/orders/{{order2_id}}/reset-otp", tc="TC-M6-010", rule="R6.4,R8.2", token="token_admin")
req("Correct OTP delivers the order", "POST", "/delivery/orders/{{order2_id}}/deliver", tc="TC-M6-010", rule="R6.4", token="token_driver1", body={"otp": "0000"},
    pre='pm.request.body.update(JSON.stringify({otp: pm.collectionVariables.get("otp2")}));',
    tests='pm.test("DELIVERED", function () { pm.expect(pm.response.json().status).to.eql("DELIVERED"); });')
req("DELIVERED is terminal", "PATCH", "/admin/orders/{{order2_id}}/status", tc="TC-M6-002", rule="R6.1", token="token_admin", body={"to_status": "CONFIRMED"}, expect=409)
req("Timeline lists every transition", "GET", "/orders/{{order2_id}}", tc="TC-M6-011", rule="R6.5", token="token_c2",
    tests='pm.test("PLACED, CONFIRMED, PACKED, OUT_FOR_DELIVERY, DELIVERED in order", function () { var t = pm.response.json().audits.map(function (a) { return a.to_state; }); '
          'pm.expect(t).to.eql(["PLACED","CONFIRMED","PACKED","OUT_FOR_DELIVERY","DELIVERED"]); pm.response.json().audits.forEach(function (a) { pm.expect(a).to.have.property("actor_role"); pm.expect(a).to.have.property("timestamp"); }); });')
req("Apple stock before the cancel", "GET", "/catalog/products/1", tc="TC-M6-003", rule="R6.2",
    tests=save("stock_before_cancel", "pm.response.json().stock"))
req("Customer cancels order 1 while PLACED", "POST", "/orders/{{order1_id}}/cancel", tc="TC-M6-003", rule="R6.2", token="token_c2",
    tests='pm.test("CANCELLED", function () { pm.expect(pm.response.json().status).to.eql("CANCELLED"); });')
req("Cancelled order restored the stock", "GET", "/catalog/products/1", tc="TC-M6-003", rule="R6.2", token="token_c2",
    tests='pm.test("stock restored by the 2 cancelled units", function () { pm.expect(pm.response.json().stock).to.eql(pm.collectionVariables.get("stock_before_cancel") + 2); });')
req("Cancelling again is a conflict", "POST", "/orders/{{order1_id}}/cancel", tc="API-ORD", rule="R6.2", token="token_c2", expect=409)
req("CANCELLED is terminal", "PATCH", "/admin/orders/{{order1_id}}/status", tc="TC-M6-015", rule="R6.1", token="token_admin", body={"to_status": "CONFIRMED"}, expect=409)
req("Admin confirms order 3", "PATCH", "/admin/orders/{{order3_id}}/status", tc="TC-M6-014", rule="R6.3", token="token_admin", body={"to_status": "CONFIRMED"})
req("Customer cancels order 3 while CONFIRMED", "POST", "/orders/{{order3_id}}/cancel", tc="TC-M6-014", rule="R6.2", token="token_c2",
    tests='pm.test("CANCELLED", function () { pm.expect(pm.response.json().status).to.eql("CANCELLED"); });')
req("Another customer cannot cancel the order", "POST", "/orders/{{order2_id}}/cancel", tc="TC-M6-012", rule="R6.6", token="token_c1", expect=403)

# ----------------------------------------------------------------------------------------------------------
folder("08 Reviews (M7)")
req("Review a product from a delivered order", "POST", "/reviews", tc="TC-M7-001", rule="R7.1", token="token_c2", body={"product_id": 1, "rating": 5, "comment": "Fresh and crisp"}, expect=201,
    tests='pm.test("review shape", function () { var b = pm.response.json(); pm.expect(b.rating).to.eql(5); pm.expect(b.user_name).to.be.a("string"); });')
req("Review the same product twice", "POST", "/reviews", tc="TC-M7-003", rule="R7.1", token="token_c2", body={"product_id": 1, "rating": 4}, expect=409)
req("Review a product never delivered", "POST", "/reviews", tc="TC-M7-002", rule="R7.1", token="token_c2", body={"product_id": 2, "rating": 4}, expect=400)
req("Comment of 301 characters", "POST", "/reviews", tc="TC-M7-004", rule="R7.1", token="token_c2", body={"product_id": 1, "rating": 4, "comment": "x" * 301}, expect=422)
req("Rating 6", "POST", "/reviews", tc="API-REV", rule="R7.1", token="token_c2", body={"product_id": 1, "rating": 6}, expect=422)
req("Rating 0", "POST", "/reviews", tc="API-REV", rule="R7.1", token="token_c2", body={"product_id": 1, "rating": 0}, expect=422)
req("Review without a token", "POST", "/reviews", tc="API-REV", rule="R7.1", body={"product_id": 1, "rating": 5}, expect=401)
req("List reviews (public)", "GET", "/reviews", tc="TC-M7-001", rule="R7.1", query={"product_id": "1"},
    tests='pm.test("contains the review", function () { var b = pm.response.json(); pm.expect(b.length).to.eql(1); pm.expect(b[0].comment).to.eql("Fresh and crisp"); });')
req("Average rating on the product", "GET", "/catalog/products/1", tc="TC-M7-001", rule="R7.1",
    tests='pm.test("avg_rating 5", function () { pm.expect(parseFloat(pm.response.json().avg_rating)).to.eql(5); });')

# ----------------------------------------------------------------------------------------------------------
folder("09 Admin (M8) and banners")
req("List orders", "GET", "/admin/orders", tc="TC-M8-005", rule="R8.2", token="token_admin",
    tests='pm.test("array of orders", function () { pm.expect(pm.response.json().length).to.be.at.least(3); });')
req("Filter orders by status DELIVERED", "GET", "/admin/orders", tc="TC-M8-005", rule="R8.2", token="token_admin", query={"status": "DELIVERED"},
    tests='pm.test("only DELIVERED", function () { var b = pm.response.json(); pm.expect(b.length).to.be.above(0); b.forEach(function (o) { pm.expect(o.status).to.eql("DELIVERED"); }); });')
req("Filter orders by an invalid status", "GET", "/admin/orders", tc="API-ADM", rule="R8.2", token="token_admin", query={"status": "NOPE"}, expect=422)
req("Orders list as a customer", "GET", "/admin/orders", tc="TC-M1-017", rule="R1.6", token="token_c2", expect=403)
req("Orders list as a driver", "GET", "/admin/orders", tc="API-ADM", rule="R1.6", token="token_driver1", expect=403)
req("Orders list without a token", "GET", "/admin/orders", tc="API-ADM", rule="R1.6", expect=401)
req("Create a product", "POST", "/admin/products", tc="TC-M8-001", rule="R8.1,R2.2", token="token_admin",
    body={"name": "Kiwi", "price": "90.00", "stock": 50, "unit": "pc", "category_id": 1, "active": True}, expect=201,
    tests=save("kiwi_id", "pm.response.json().id"))
req("Create a product with price 0.00", "POST", "/admin/products", tc="TC-M8-002", rule="R2.2", token="token_admin",
    body={"name": "Bad", "price": "0.00", "stock": 5, "unit": "pc", "category_id": 1}, expect=422)
req("Create a product with price 10000.01", "POST", "/admin/products", tc="TC-M8-002", rule="R2.2", token="token_admin",
    body={"name": "Bad", "price": "10000.01", "stock": 5, "unit": "pc", "category_id": 1}, expect=422)
req("Create a product with stock 1001", "POST", "/admin/products", tc="TC-M8-002", rule="R2.2", token="token_admin",
    body={"name": "Bad", "price": "10.00", "stock": 1001, "unit": "pc", "category_id": 1}, expect=422)
req("Create a product with a bad unit", "POST", "/admin/products", tc="TC-M8-002", rule="R2.2", token="token_admin",
    body={"name": "Bad", "price": "10.00", "stock": 5, "unit": "bucket", "category_id": 1}, expect=422)
req("Create a product as a customer", "POST", "/admin/products", tc="API-ADM", rule="R1.6", token="token_c2",
    body={"name": "Kiwi2", "price": "90.00", "stock": 50, "unit": "pc", "category_id": 1}, expect=403)
req("Update a product", "PUT", "/admin/products/{{kiwi_id}}", tc="API-ADM", rule="R8.1", token="token_admin", body={"price": "95.00"},
    tests='pm.test("price updated", function () { pm.expect(pm.response.json().price).to.eql("95.00"); });')
req("Update an unknown product", "PUT", "/admin/products/999999", tc="API-ADM", rule="R8.1", token="token_admin", body={"price": "95.00"}, expect=404)
req("Update stock", "PATCH", "/admin/products/{{kiwi_id}}/stock", tc="TC-M8-003", rule="R8.1", token="token_admin", body={"stock": 5},
    tests='pm.test("stock 5", function () { pm.expect(pm.response.json().stock).to.eql(5); });')
req("Update stock to -1", "PATCH", "/admin/products/{{kiwi_id}}/stock", tc="TC-M8-003", rule="R2.2", token="token_admin", body={"stock": -1}, expect=422)
req("Public catalog shows the new stock", "GET", "/catalog/products/{{kiwi_id}}", tc="TC-M8-003", rule="R8.1",
    tests='pm.test("stock 5", function () { pm.expect(pm.response.json().stock).to.eql(5); });')
req("Deactivate the product", "PATCH", "/admin/products/{{kiwi_id}}/active", tc="TC-M8-004", rule="R8.1", token="token_admin", body={"active": False},
    tests='pm.test("inactive", function () { pm.expect(pm.response.json().active).to.eql(false); });')
req("Inactive product is hidden (detail)", "GET", "/catalog/products/{{kiwi_id}}", tc="TC-M2-007", rule="R2.4", expect=404)
req("Inactive product is hidden (search)", "GET", "/catalog/products", tc="TC-M2-007", rule="R2.4", query={"search": "Kiwi"},
    tests='pm.test("no results", function () { pm.expect(pm.response.json().items.length).to.eql(0); });')
req("Admin product list still shows inactive", "GET", "/admin/products", tc="TC-M8-004", rule="R8.1", token="token_admin", query={"search": "Kiwi"},
    tests='pm.test("Kiwi listed", function () { pm.expect(pm.response.json().items ? pm.response.json().items.length : pm.response.json().length).to.be.above(0); });')
req("List coupons", "GET", "/admin/coupons", tc="API-ADM", rule="R8.3", token="token_admin",
    tests='pm.test("4 coupons incl. OLD20", function () { var b = pm.response.json(); pm.expect(b.length).to.eql(4); var f = b.filter(function (c) { return c.code === "FLAT50"; })[0]; '
          'pm.collectionVariables.set("flat50_id", f.id); });')
req("Disable FLAT50", "PATCH", "/admin/coupons/{{flat50_id}}", tc="TC-M8-006", rule="R8.3", token="token_admin", body={"active": False},
    tests='pm.test("disabled", function () { pm.expect(pm.response.json().active).to.eql(false); });')
req("Customer cart for the disabled-coupon check", "POST", "/cart/items", tc="TC-M8-006", rule="R3.1", token="token_c2", body={"product_id": 1, "quantity": 5})
req("Disabled coupon is rejected", "POST", "/cart/coupon", tc="TC-M8-006", rule="R8.3,R4.2", token="token_c2", body={"code": "FLAT50"}, expect=400)
req("Public offers no longer list it", "GET", "/catalog/offers", tc="TC-M9-006", rule="R9.3",
    tests='pm.test("FLAT50 absent", function () { pm.expect(pm.response.json().map(function (c) { return c.code; })).to.not.include("FLAT50"); });')
req("Re-enable FLAT50", "PATCH", "/admin/coupons/{{flat50_id}}", tc="TC-M8-006", rule="R8.3", token="token_admin", body={"active": True})
req("Clear customer2 cart", "DELETE", "/cart", tc="API-ADM", rule="R3.4", token="token_c2")
req("List users", "GET", "/admin/users", tc="API-ADM", rule="R8.3", token="token_admin",
    tests='pm.test("users listed, ids resolved", function () { var b = pm.response.json(); pm.expect(b.length).to.be.at.least(5); '
          'function id(e) { return b.filter(function (u) { return u.email === e; })[0].id; } '
          'pm.collectionVariables.set("jane_id", id("jane.doe@example.com")); '
          'pm.expect(b.filter(function (u) { return u.email === "jane.doe@example.com"; })[0].status).to.eql("LOCKED"); });')
req("Admin unlocks the locked user", "POST", "/admin/users/{{jane_id}}/unlock", tc="TC-M8-007", rule="R1.5,R8.3", token="token_admin",
    tests='pm.test("ACTIVE", function () { pm.expect(pm.response.json().status).to.eql("ACTIVE"); });')
req("Unlocked user can log in", "POST", "/auth/login", tc="TC-M8-007", rule="R1.5,R8.3", body={"email": "jane.doe@example.com", "password": "Passw0rd1"})
req("Admin locks a user", "POST", "/admin/users/{{jane_id}}/lock", tc="TC-M8-007", rule="R8.3", token="token_admin",
    tests='pm.test("LOCKED", function () { pm.expect(pm.response.json().status).to.eql("LOCKED"); });')
req("Locked user cannot log in", "POST", "/auth/login", tc="TC-M8-007", rule="R1.5,R8.3", body={"email": "jane.doe@example.com", "password": "Passw0rd1"}, expect=401)
req("Lock an unknown user", "POST", "/admin/users/999999/lock", tc="API-ADM", rule="R8.3", token="token_admin", expect=404)
req("Dashboard", "GET", "/admin/dashboard", tc="TC-M8-008", rule="R8.4", token="token_admin",
    tests='pm.test("orders today and revenue > 0, low stock list", function () { var b = pm.response.json(); pm.expect(b.orders_today).to.be.above(0); '
          'pm.expect(parseFloat(b.revenue_today)).to.be.above(0); pm.expect(b.low_stock_products).to.be.an("array"); '
          'b.low_stock_products.forEach(function (p) { pm.expect(p.stock).to.be.below(10); }); });')
req("Dashboard as a customer", "GET", "/admin/dashboard", tc="API-ADM", rule="R1.6", token="token_c2", expect=403)
req("Audit log filtered by order", "GET", "/admin/audit-log", tc="TC-M8-010", rule="R8.5", token="token_admin", query={"order_id": "{{order2_id}}"},
    tests='pm.test("only that order, chronological", function () { var b = pm.response.json(); pm.expect(b.length).to.eql(5); '
          'b.forEach(function (a, i) { pm.expect(a.order_id).to.eql(parseInt(pm.collectionVariables.get("order2_id"))); if (i) { pm.expect(a.timestamp >= b[i - 1].timestamp).to.eql(true); } }); });')
req("Audit log as a customer", "GET", "/admin/audit-log", tc="API-ADM", rule="R1.6", token="token_c2", expect=403)
req("Admin lists banners incl. inactive", "GET", "/admin/banners", tc="TC-M9-005", rule="R9.2", token="token_admin")
req("Create an inactive banner", "POST", "/admin/banners", tc="TC-M9-004", rule="R9.2", token="token_admin",
    body={"title": "Hidden banner", "image_url": "https://example.com/b.png", "link_url": "/", "display_order": 99, "active": False}, expect=201,
    tests=save("banner_id", "pm.response.json().id"))
req("Inactive banner is not public", "GET", "/banners", tc="TC-M9-004", rule="R9.2",
    tests='pm.test("hidden banner absent", function () { pm.expect(pm.response.json().map(function (b) { return b.title; })).to.not.include("Hidden banner"); });')
req("Create a banner with a 1-character title", "POST", "/admin/banners", tc="TC-M9-005", rule="R9.2", token="token_admin",
    body={"title": "X", "image_url": "https://example.com/b.png"}, expect=422)
req("Activate the banner", "PUT", "/admin/banners/{{banner_id}}", tc="TC-M9-005", rule="R9.2", token="token_admin", body={"active": True},
    tests='pm.test("active", function () { pm.expect(pm.response.json().active).to.eql(true); });')
req("Banner is now public", "GET", "/banners", tc="TC-M9-004", rule="R9.2",
    tests='pm.test("shown", function () { pm.expect(pm.response.json().map(function (b) { return b.title; })).to.include("Hidden banner"); });')
req("Delete the banner", "DELETE", "/admin/banners/{{banner_id}}", tc="TC-M9-005", rule="R9.2", token="token_admin", expect=204)
req("Delete it again", "DELETE", "/admin/banners/{{banner_id}}", tc="TC-M9-005", rule="R9.2", token="token_admin", expect=404)
req("Update an unknown banner", "PUT", "/admin/banners/999999", tc="API-ADM", rule="R9.2", token="token_admin", body={"active": True}, expect=404)
req("Banner management as a customer", "POST", "/admin/banners", tc="API-ADM", rule="R1.6", token="token_c2",
    body={"title": "Nope", "image_url": "https://example.com/b.png"}, expect=403)

# ----------------------------------------------------------------------------------------------------------
folder("10 Rate limiting (R1.7)")
req("Wait for a clean limiter window", "GET", "/health", tc="TC-M1-018", rule="R1.7",
    pre='setTimeout(function () {}, 61500);', tests=save("rl_hits", '"[]"'))
req("11th login in a minute is rate-limited", "POST", "/auth/login", tc="TC-M1-018", rule="R1.7",
    body={"email": "customer2@freshcart.test", "password": "WrongPass1"}, expect=429, headers={"X-Skip-Throttle": "1"},
    pre="""
var base = pm.variables.get("base_url");
var n = 0;
function fire() {
  if (n >= 10) { return; }
  n++;
  pm.sendRequest({url: base + "/auth/login", method: "POST", header: {"Content-Type": "application/json"},
    body: {mode: "raw", raw: JSON.stringify({email: "customer2@freshcart.test", password: "WrongPass1"})}}, function () { fire(); });
}
fire();
""",
    tests='pm.test("Retry-After header present", function () { pm.expect(pm.response.headers.get("Retry-After")).to.match(/^\\d+$/); });')


# ----------------------------------------------------------------------------------------------------------
def build():
    coll = {
        "info": {"name": "FreshCart API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                 "description": "API tests for FreshCart. Run against the test-mode backend: "
                                "APP_ENV=test FIXED_NOW=2026-11-10T09:00:00. First request resets the database."},
        "event": [{"listen": "prerequest", "script": {"type": "text/javascript", "exec": COLLECTION_PRE.strip().split("\n")}}],
        "variable": [{"key": "rl_hits", "value": "[]"}],
        "item": [{"name": n, "item": items} for n, items in folders],
    }
    env = {"id": "freshcart-local", "name": "FreshCart local (test mode)",
           "values": [{"key": "base_url", "value": "http://localhost:8000/api", "enabled": True}],
           "_postman_variable_scope": "environment"}
    (HERE / "FreshCart.postman_collection.json").write_text(json.dumps(coll, indent=2), encoding="utf-8")
    (HERE / "FreshCart.postman_environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    total = sum(len(i) for _, i in folders)
    print("folders", len(folders), "requests", total)
    for n, i in folders:
        print(f"  {n}: {len(i)}")


if __name__ == "__main__":
    build()

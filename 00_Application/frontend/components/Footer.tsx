import Link from "next/link";

export default function Footer() {
  return (
    <footer id="site-footer" data-testid="site-footer" className="mt-auto bg-ink pb-20 pt-10 text-gray-300 sm:pb-10">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-4 sm:grid-cols-4">
        <div className="col-span-2 sm:col-span-1">
          <h3 className="mb-2 border-b-2 border-accent-500 pb-1 text-sm font-bold uppercase tracking-wide text-white">
            FreshCart
          </h3>
          <p className="mt-3 text-sm text-gray-400">
            Fresh groceries, delivered. Quality products, fair prices, and reliable delivery slots you can count on.
          </p>
        </div>

        <div>
          <h3 className="mb-2 border-b-2 border-accent-500 pb-1 text-sm font-bold uppercase tracking-wide text-white">Shop</h3>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <Link href="/" className="hover:text-accent-400">
                Catalog
              </Link>
            </li>
            <li>
              <Link href="/cart" className="hover:text-accent-400">
                Cart
              </Link>
            </li>
            <li>
              <Link href="/orders" className="hover:text-accent-400">
                My Orders
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="mb-2 border-b-2 border-accent-500 pb-1 text-sm font-bold uppercase tracking-wide text-white">Support</h3>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="text-gray-400">Help Center</li>
            <li className="text-gray-400">Delivery Info</li>
          </ul>
        </div>

        <div>
          <h3 className="mb-2 border-b-2 border-accent-500 pb-1 text-sm font-bold uppercase tracking-wide text-white">Admin</h3>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <Link id="footer-admin-link" data-testid="footer-admin-link" href="/admin" className="hover:text-accent-400">
                Admin Dashboard
              </Link>
            </li>
            <li>
              <Link href="/delivery" className="hover:text-accent-400">
                Delivery Portal
              </Link>
            </li>
          </ul>
        </div>
      </div>

      <div className="mx-auto mt-8 max-w-6xl border-t border-white/10 px-4 pt-4 text-xs text-gray-500">
        © {new Date().getFullYear()} FreshCart. Software Testing portfolio project.
      </div>
    </footer>
  );
}

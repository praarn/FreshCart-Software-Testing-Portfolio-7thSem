export type Role = "CUSTOMER" | "ADMIN" | "DELIVERY_PARTNER";
export type UserStatus = "ACTIVE" | "LOCKED";
export type ProductUnit = "kg" | "g" | "l" | "ml" | "pc" | "pack";
export type OrderStatus = "PLACED" | "CONFIRMED" | "PACKED" | "OUT_FOR_DELIVERY" | "DELIVERED" | "CANCELLED";
export type PaymentMethod = "COD" | "UPI" | "CARD";
export type CouponType = "PERCENT" | "FLAT";

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: Role;
  status: UserStatus;
}

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: string;
  stock: number;
  unit: ProductUnit;
  category_id: number;
  category_name: string;
  active: boolean;
  avg_rating: number | null;
}

export interface ProductListResponse {
  items: Product[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  product_name: string;
  unit: ProductUnit;
  unit_price: string;
  quantity: number;
  stock: number;
  line_total: string;
}

export interface Cart {
  items: CartItem[];
  coupon_code: string | null;
  subtotal: string;
  discount: string;
  delivery_fee: string;
  total: string;
}

export interface Slot {
  slot_start: string;
  slot_end: string;
  available: boolean;
  remaining_capacity: number;
}

export interface OrderItem {
  product_id: number;
  product_name: string;
  unit: ProductUnit;
  unit_price: string;
  quantity: number;
  line_total: string;
}

export interface AuditEntry {
  from_state: string | null;
  to_state: string;
  actor_role: string;
  timestamp: string;
}

export interface Order {
  id: number;
  order_number: string;
  status: OrderStatus;
  subtotal: string;
  discount: string;
  delivery_fee: string;
  total: string;
  coupon_code: string | null;
  address_line1: string;
  address_city: string;
  address_pincode: string;
  slot_start: string;
  slot_end: string;
  payment_method: PaymentMethod;
  payment_reference: string | null;
  delivery_otp: string | null;
  delivery_partner_id: number | null;
  items: OrderItem[];
  created_at: string;
  audits: AuditEntry[];
}

export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  user_name: string;
  rating: number;
  comment: string | null;
  created_at: string;
}

export interface Coupon {
  id: number;
  code: string;
  type: CouponType;
  value: string;
  min_subtotal: string;
  max_discount: string | null;
  first_order_only: boolean;
  valid_weekdays: string | null;
  active: boolean;
  expires_at: string | null;
}

export interface Dashboard {
  orders_today: number;
  revenue_today: string;
  low_stock_products: { id: number; name: string; stock: number }[];
}

export interface AuditLogEntry {
  id: number;
  order_id: number;
  from_state: string | null;
  to_state: string;
  actor_id: number | null;
  actor_role: string;
  timestamp: string;
}

export interface FieldError {
  field: string;
  message: string;
}

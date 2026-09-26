# LabLine Frontend — Clinical Portal & Spatial Design System

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Glassmorphism](https://img.shields.io/badge/UI_Style-Spatial_Glassmorphism-6366F1?style=for-the-badge)](https://developer.mozilla.org)

The **LabLine Frontend** is a zero-build-step, high-performance static web application delivering clinical diagnostic portals for **Patients**, **Laboratory Technicians**, and **Pathology Administrators**. Built with pure vanilla JavaScript (ES6+), semantic HTML5, and a custom dark-mode spatial glassmorphism design system.

---

## Directory Architecture

```plaintext
frontend/
├── admin/
│   ├── assign.html            # Specimen queue technician dispatch portal
│   ├── catalog-manage.html    # Diagnostic test catalog & reference interval editor
│   └── dashboard.html         # Lab operations analytics & KPI metric cards
├── css/
│   └── style.css              # Custom spatial design system, tokens, gradients & micro-animations
├── js/
│   ├── auth-guard.js          # Role-Based client-side navigation guard
│   ├── shared.js              # Central LabStore API client, session lifecycle, and helpers
│   └── tailwind.config.js     # Extended color tokens and typography configuration
├── patient/
│   ├── catalog.html           # Diagnostic test browser, smart search & cart manager
│   ├── payment.html           # Billing checkout, address input & simulated payment
│   ├── reports.html           # Certified clinical diagnostic report viewer & print styling
│   ├── tracking.html          # Real-time 5-stage specimen tracking timeline
│   └── verify.html            # Public SHA-256 report verification portal & tamper simulator
├── technician/
│   ├── queue.html             # Incoming specimen accessioning queue & worklist
│   └── result-entry.html      # Numerical biomarker input & reference range validator
├── index.html                 # Central landing page & unified login/registration portal
└── README.md                  # Dedicated Frontend Documentation (this file)
```

---

## Core Client Modules

### 1. `LabStore` API Client (`js/shared.js`)
`LabStore` is the central singleton handling communication with the FastAPI backend:
- **`LabStore.api(endpoint, options)`**: Central wrapper injecting JWT `Authorization: Bearer <token>` headers and handling errors.
- **Session Lifecycle**: `login()`, `register()`, `logout()`, `getCurrentUser()`, and token persistence in `localStorage`.
- **Cart Management**: `getCart()`, `addToCart()`, `removeFromCart()`, `clearCart()` for patient test selections.
- **Diagnostic Catalog**: `getTests()`, `getTestById()`, `createTest()`, `updateTest()`, `deleteTest()`.
- **Order Tracking**: `getBookings()`, `getOrderById()`, `updateOrderStage()`, `assignTechnician()`, `autoDispatchWorkload()`.
- **Result & Report Operations**: `submitResults()`, `certifyResults()`, `getReportData()`, `verifyReportIntegrity()`.

### 2. Client-Side Authentication Guard (`js/auth-guard.js`)
- Runs synchronously before page rendering.
- Inspects JWT session token and role claims (`patient`, `technician`, `admin`).
- Blocks unauthorized role access (e.g., prevents patients from loading `/admin/dashboard.html` or technicians from accessing unauthorized paths) and redirects to `/index.html`.

### 3. Cryptographic Hashing & Verification
- **`computeCanonicalReportPayload(order, testsList)`**: Constructs a deterministic JSON string matching the backend's canonical serialization.
- **`generateOrderReportHash(order, testsList)`**: Computes the SHA-256 digest using the browser's native `window.crypto.subtle.digest` API.
- **`verifyOrderIntegrity(order, testsList)`**: Evaluates whether the calculated digest matches `order.report_hash`.

### 4. Smart Prescription Parsing
- Client-side keyword extraction matching physician notes against the clinical catalog using fuzzy and substring scoring algorithms.

---

## Design System & Aesthetics

### 1. Color Palette Tokens
- **Backgrounds**: Slate Deep (`#090D16`), Card Elevated (`#111827`), Surface Glass (`rgba(17, 24, 39, 0.75)`)
- **Accents**: Cyan Clinical (`#06B6D4`), Violet Glow (`#8B5CF6`), Emerald Safe (`#10B981`), Amber Warning (`#F59E0B`), Rose Critical (`#F43F5E`)
- **Clinical Specimen Tube Caps**:
  - `tube-cap-edta` (Purple): Complete Blood Count & Hematology
  - `tube-cap-serum` (Gold/Red): Lipid Profile, Thyroid, Liver & Kidney panels
  - `tube-cap-fluoride` (Gray): Fasting & Postprandial Glucose
  - `tube-cap-heparin` (Green): Arterial blood gases & plasma chemistry

### 2. Micro-Interactions & Glassmorphism
- Subtle backdrop filters (`backdrop-blur-md`) with glowing border gradients.
- Responsive biological range gauges indicating where observed clinical values fall relative to healthy populations.
- Print-optimized CSS media queries (`@media print`) stripping UI chrome for clean medical PDF reports.

---

## How to Run Locally

### Option 1: Python Built-In HTTP Server (Recommended)
```bash
cd frontend
python -m http.server 5500
```
Visit: **[http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html)**

### Option 2: VS Code Live Server
1. Open the project folder in VS Code.
2. Install the **Live Server** extension.
3. Right-click `frontend/index.html` $\rightarrow$ **Open with Live Server**.

### Option 3: Node.js `serve` / `http-server`
```bash
npx serve frontend -p 5500
```

---

## Configuration & Backend Integration

By default, the frontend connects to the local FastAPI backend at `http://127.0.0.1:8000`.

To point the frontend to a remote or production API server, edit `frontend/js/shared.js`:
```javascript
// Line 19 of js/shared.js
window.LABLINE_API_BASE = window.LABLINE_API_BASE || 'https://api.yourdomain.com';
```

Or inject it dynamically before `shared.js` loads in your HTML:
```html
<script>
  window.LABLINE_API_BASE = 'https://api.yourdomain.com';
</script>
<script src="/js/shared.js"></script>
```

---

## Static Hosting & Deployment

Since the frontend consists entirely of standard HTML, CSS, and JavaScript, it can be deployed instantly to any static hosting provider:

| Host | Deployment Method |
| :--- | :--- |
| **Vercel** | Link GitHub repository and set Root Directory to `frontend` |
| **Netlify** | Drag-and-drop the `frontend` folder or connect repository |
| **GitHub Pages** | Push contents of `frontend/` to `gh-pages` branch |
| **Nginx / Apache** | Configure document root to point to `/var/www/labline/frontend` |

---

<div align="center">
  <sub>Developed by <a href="https://github.com/nithin16-cloud">Nithin T</a></sub>
</div>

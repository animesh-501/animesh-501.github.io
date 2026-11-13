/*
  ============================================================
  SITE CONTENT — edit this file, not index.html.
  ============================================================

  To add a project: copy a block in PROJECTS, give it an id, and add the id to
  projectOrder. The first project in projectOrder is the featured one.

  Need a variant for a specific role? Add a block to FOCUS (e.g. `ops: {...}`) with only
  the fields you want to change, then send https://animesh-501.github.io/?focus=ops
  Anything a focus doesn't set falls back to FOCUS.default.
*/

const PROFILE = {
  name: 'Animesh Choubey',
  education: 'MSBA · Cal State East Bay',
  email: 'animeshkchoubey@gmail.com',
};

const DEFAULT_FOCUS = 'default';

const FOCUS = {
  default: {
    title: 'Supply Chain Analyst',
    tagline: 'Forecasts, inventory policy and supplier analytics — tested against real demand before anyone acts on them.',
    ticker: ['Supply Chain Analytics', 'Demand Forecasting', 'Safety Stock', 'OTIF', 'Supplier Scorecards', 'Inventory Policy', 'SQL · Python'],
    focusLabel: 'Supply Chain · Inventory · Procurement',
    projectOrder: ['demand-forecast', 'otif', 'procurement', 'inventory'],
    skillsPanel: 'domain',
    stats: [
      { text: '6+', label: 'Years of Experience' },
      { text: '32%', label: 'Less Stock, Same Service' },
      { text: '$24M+', label: 'Price Variance Found' },
    ],
    contactLine: 'Open to Supply Chain, Demand Planning, Procurement and Operations Analyst roles.',
  },
};

const GH = 'https://github.com/animesh-501/';

const PROJECTS = {
  'demand-forecast': {
    title: 'Demand Forecasting<br />&amp; Safety Stock Optimization',
    badge: 'Forecasting · Inventory',
    desc: 'Weekly forecasts for 500 SKU-locations, safety stock set from each one\'s measured forecast error, then a full year of real demand replayed week by week. To stay in stock 95% of weeks, the LightGBM forecast needed 32% less inventory than a 4-week moving average and 6% less than "same week last year" — and most of its edge was correcting for growth.',
    metrics: [
      ['4.4%', 'Forecast error (WAPE)'],
      ['−32%', 'Stock vs moving avg'],
      ['500', 'SKU-locations'],
      ['52 wk', 'Out-of-sample replay'],
    ],
    tags: ['Python', 'SQL', 'DuckDB', 'LightGBM', 'SciPy', 'pandas'],
    impact: [
      ['WAPE: moving average', '11.1%'],
      ['WAPE: same week last year', '6.2%'],
      ['WAPE: LightGBM', '4.4%', true],
      ['Stock for 95% in-stock: moving avg', '~199K units'],
      ['Stock for 95% in-stock: LightGBM', '~136K units', true],
      ['Policy', 'Weekly review, 2-wk lead time'],
    ],
    note: 'Public retail data · 913K daily sales rows',
    link: GH + 'demand-forecast-safety-stock',
  },

  otif: {
    title: 'OTIF Root-Cause Analysis',
    badge: 'Logistics',
    desc: 'Only 41% of 65,752 orders arrived on time and in full. Chi-square tests and a model check ruled out region, product, customer and timing: lateness came from promises set shorter than real transit. First Class promised 1 day and always took 2; Second Class shipped no faster than Standard. Fixing the promises alone takes OTIF from 41% to 80%.',
    metrics: [
      ['41% → 80%', 'OTIF, promise fixes only'],
      ['65.8K', 'Orders'],
      ['27', 'Driver tests'],
      ['0.774', 'AUC: 2 rules = 14-feature model'],
    ],
    tags: ['SQL', 'DuckDB', 'Python', 'SciPy', 'scikit-learn', 'LightGBM'],
    impact: [],
    note: '',
    link: GH + 'otif-delivery-risk',
  },

  procurement: {
    title: 'Procurement Spend &amp; Supplier Scorecard',
    badge: 'Procurement',
    desc: '$1.63B of purchases benchmarked line by line against each item\'s median price: $24–35M paid above it. A third of that sits with 5 vendors holding 8% of spend. The two largest suppliers price at the median but deliver only 86–87% on time, so the fix there is delivery performance.',
    metrics: [
      ['$24–35M', 'Above-benchmark spend'],
      ['24', 'Suppliers scored'],
      ['73%', 'Spend in top 5 vendors'],
    ],
    tags: ['SQL', 'DuckDB', 'Python', 'pandas'],
    impact: [],
    note: '',
    link: GH + 'procurement-spend-scorecard',
  },

  inventory: {
    title: 'Inventory ABC/XYZ &amp; Policy Test',
    badge: 'Inventory',
    desc: '4,163 SKUs segmented and replayed through a year of real transactions. Textbook ABC/XYZ service targets saved under 1%; data-tuned targets overfit. The real waste: 16% of stock sat on items that never sold again. Stopping reorders after 8 quiet weeks cut inventory 12.6% for $2.9K of lost sales.',
    metrics: [
      ['−12.6%', 'Inventory'],
      ['4,163', 'SKUs'],
      ['1.07M', 'Transactions'],
    ],
    tags: ['SQL', 'DuckDB', 'Python', 'NumPy', 'SciPy'],
    impact: [],
    note: '',
    link: GH + 'inventory-abc-xyz-optimization',
  },
};

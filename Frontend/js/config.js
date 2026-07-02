/* ============================================================================
   ArmWork Frontend Config

   GitHub Pages-ից բացելիս frontend-ը պետք է իմանա backend API-ի public URL-ը։
   Docker backend-ը local բացվում է http://127.0.0.1:5050 հասցեով, իսկ ինտերնետի համար
   սովորաբար օգտագործում ենք ngrok, օրինակ՝ https://abc.ngrok-free.app/api։
   ============================================================================ */

window.ARMWORK_CONFIG.API_BASE_URL = "https://cadet-second-reheat.ngrok-free.dev";

// Local Flask/Docker server-ից բացելիս թող դատարկ։
// GitHub Pages publish անելիս այստեղ դիր ngrok-ի API URL-ը։
window.ARMWORK_CONFIG.API_BASE_URL = "";

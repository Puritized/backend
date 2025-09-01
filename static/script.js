const API_BASE = ""; // same origin when hosted on Render

// UI helpers
const $ = (s) => document.querySelector(s);

// Tabs
const tabs = { home: $("#tabHome"), recipes: $("#tabRecipes"), favorites: $("#tabFavorites"), premium: $("#tabPremium") };
const views = { home: $("#homeView"), recipes: $("#recipesView"), favorites: $("#favoritesView"), premium: $("#premiumView") };
let token = null;
let is_premium = false;

function switchTab(tab){
  Object.values(tabs).forEach(t => t.classList.remove("active"));
  Object.values(views).forEach(v => v.style.display = "none");
  tabs[tab].classList.add("active");
  views[tab].style.display = "block";
}
tabs.home.onclick = () => switchTab("home");
tabs.recipes.onclick = () => switchTab("recipes");
tabs.favorites.onclick = () => switchTab("favorites");
tabs.premium.onclick = () => switchTab("premium");

// Auth
$("#btnRegister").onclick = async () => {
  const email = $("#email").value, password = $("#password").value;
  const r = await fetch("/api/auth/register", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email, password})});
  const data = await r.json();
  alert(data.msg || data.error || "Registered");
}

$("#btnLogin").onclick = async () => {
  const email = $("#email").value, password = $("#password").value;
  const r = await fetch("/api/auth/login", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email, password})});
  const data = await r.json();
  if(data.token){
    token = data.token;
    is_premium = data.is_premium;
    $("#status").textContent = "Logged in";
    alert("Logged in");
  } else {
    alert(data.error || "Login failed");
  }
}

// Get free recipes
$("#btnGetRecipes").onclick = async () => {
  const ingredients = $("#ingredients").value;
  $("#recipesList").innerHTML = "Loading...";
  const r = await fetch("/api/recipes", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ingredients, number:5})});
  const data = await r.json();
  $("#recipesList").innerHTML = "";
  if(data.recipes && data.recipes.length){
    data.recipes.forEach(rp => {
      const div = document.createElement("div");
      div.className = "recipe-card";
      div.innerHTML = `<h3>${rp.name || rp.title || rp.recipe_name || ""}</h3>
                       <p><strong>Ingredients:</strong> ${(rp.ingredients||[]).join(", ")}</p>
                       <p><strong>Instructions:</strong> ${rp.instructions || ""}</p>
                       <button class="save">Save</button>`;
      div.querySelector(".save").onclick = () => saveFavorite(rp);
      $("#recipesList").appendChild(div);
    });
  } else {
    $("#recipesList").innerHTML = "No recipes found.";
  }
}

async function saveFavorite(rp){
  if(!token) return alert("Please login to save favorites");
  const payload = {
    recipe_name: rp.name || rp.title || rp.recipe_name || "Untitled",
    ingredients: rp.ingredients || [],
    instructions: rp.instructions || ""
  };
  const r = await fetch("/api/favorites/add", {method:"POST", headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`}, body: JSON.stringify(payload)});
  const data = await r.json();
  if(r.status===201) alert("Saved to favorites");
  else alert(data.error || "Failed");
}

// Load favorites
$("#btnLoadFavs").onclick = async () => {
  if(!token) return alert("Please login");
  const r = await fetch("/api/favorites/list", {headers:{"Authorization":`Bearer ${token}`}});
  const data = await r.json();
  $("#favList").innerHTML = "";
  data.forEach(f => {
    const div = document.createElement("div");
    div.className = "recipe-card";
    div.innerHTML = `<h3>${f.recipe_name}</h3><p><strong>Ingredients:</strong> ${f.ingredients.join(", ")}</p><p>${f.instructions}</p>`;
    $("#favList").appendChild(div);
  });
}

// Premium: unlock via Paystack
$("#btnUnlock").onclick = async () => {
  if(!token) return alert("Please login first (Paystack needs email)");
  // Get user email from token? Backend expects email param. For simplicity ask user email:
  const email = prompt("Enter your account email (used for Paystack):");
  if(!email) return;
  const r = await fetch("/api/payments/checkout", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email})});
  const data = await r.json();
  if(data.authorization_url){
    window.location.href = data.authorization_url;
  } else {
    alert("Paystack init failed");
  }
}

// When premium tab opened, try to load premium recipes if user is premium
tabs.premium.onclick = async () => {
  if(!token) {
    $("#premiumStatus").textContent = "Please login to access premium.";
    return;
  }
  if(!is_premium) {
    $("#premiumStatus").textContent = "Premium locked. Unlock with Paystack.";
    return;
  }
  $("#premiumStatus").textContent = "Loading premium recipes...";
  const ingredients = prompt("Enter ingredients for premium recipes (comma separated):", "chicken, rice");
  const r = await fetch("/api/premium/recipes", {method:"POST", headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`}, body: JSON.stringify({ingredients, number:3})});
  const data = await r.json();
  $("#premiumList").innerHTML = "";
  if(data.recipes){
    data.recipes.forEach(rp => {
      const div = document.createElement("div");
      div.className = "recipe-card";
      div.innerHTML = `<h3>${rp.name}</h3><p><strong>Ingredients:</strong> ${(rp.ingredients||[]).join(", ")}</p><p>${rp.instructions||rp.steps||""}</p>`;
      $("#premiumList").appendChild(div);
    });
  } else {
    $("#premiumList").innerHTML = "No premium recipes available.";
  }
}

// set initial tab
switchTab("home");
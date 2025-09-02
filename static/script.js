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
  const r = await fetch("/api/auth/register", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({email, password})
  });
  const data = await r.json();
  alert(data.message || data.error || "Registered");
}

$("#btnLogin").onclick = async () => {
  const email = $("#email").value, password = $("#password").value;
  const r = await fetch("/api/auth/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({email, password})
  });
  const data = await r.json();

  if(r.status === 200){
    // No token returned now, just mark as logged in
    token = "logged-in"; 
    $("#status").textContent = "Logged in";
    alert(data.message || "Login successful");
  } else {
    alert(data.error || "Login failed");
  }
}

// Get free recipes
$("#btnGetRecipes").onclick = async () => {
  const ingredientsInput = $("#ingredients").value;
  $("#recipesList").innerHTML = "Loading...";

  try {
    const r = await fetch("/api/recipes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // always send ingredients as array
      body: JSON.stringify({ ingredients: ingredientsInput.split(",").map(i => i.trim()), number: 5 })
    });

    if (!r.ok) throw new Error("Server error " + r.status);

    const data = await r.json();
    $("#recipesList").innerHTML = "";

    if (data.recipes && data.recipes.length) {
      data.recipes.forEach(rp => {
        let name, ingr, instructions;

        if (typeof rp === "string") {
          // fallback plain text recipe
          name = "Generated Recipe";
          ingr = ingredientsInput.split(",").map(i => i.trim());
          instructions = rp;
        } else {
          // structured recipe object
          name = rp.name || rp.title || rp.recipe_name || "Untitled";
          ingr = Array.isArray(rp.ingredients)
            ? rp.ingredients
            : (typeof rp.ingredients === "string"
                ? rp.ingredients.split(",")
                : []);
          instructions = rp.instructions || rp.steps || "";
        }

        const div = document.createElement("div");
        div.className = "recipe-card";
        div.innerHTML = `<h3>${name}</h3>
                         <p><strong>Ingredients:</strong> ${ingr.join(", ")}</p>
                         <p><strong>Instructions:</strong> ${instructions}</p>
                         <button class="save">Save</button>`;
        div.querySelector(".save").onclick = () => saveFavorite({ name, ingredients: ingr, instructions });
        $("#recipesList").appendChild(div);
      });
    } else {
      $("#recipesList").innerHTML = "No recipes found.";
    }
  } catch (err) {
    console.error("Error fetching recipes:", err);
    $("#recipesList").innerHTML = " Could not load recipes. Try again.";
  }
};


async function saveFavorite(rp){
  if(!token) return alert("Please login to save favorites");

  try {
    const payload = {
      recipe_name: rp.name,
      ingredients: rp.ingredients,
      instructions: rp.instructions
    };

    const r = await fetch("/api/favorites/add", {
      method:"POST",
      headers:{
        "Content-Type":"application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!r.ok) {
      const errorData = await r.json().catch(() => ({}));
      throw new Error(errorData.error || `Request failed with ${r.status}`);
    }

    const data = await r.json();
    alert(data.message || "Saved to favorites");

  } catch (err) {
    console.error("Error saving favorite:", err);
    alert(" Could not save favorite: " + err.message);
  }
}

// Load favorites
$("#btnLoadFavs").onclick = async () => {
  if(!token) return alert("Please login");
  const r = await fetch("/api/favorites/list");
  const data = await r.json();
  $("#favList").innerHTML = "";
  data.forEach(f => {
    const ingredients = Array.isArray(f.ingredients) ? f.ingredients : (typeof f.ingredients === "string" ? f.ingredients.split(",") : []);
    const div = document.createElement("div");
    div.className = "recipe-card";
    div.innerHTML = `<h3>${f.recipe_name}</h3>
                     <p><strong>Ingredients:</strong> ${ingredients.join(", ")}</p>
                     <p>${f.instructions}</p>`;
    $("#favList").appendChild(div);
  });
}

// Premium: unlock via Paystack
$("#btnUnlock").onclick = async () => {
  if(!token) return alert("Please login first (Paystack needs email)");
  const email = prompt("Enter your account email (used for Paystack):");
  if(!email) return;
  const r = await fetch("/api/payments/checkout", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({email})
  });
  const data = await r.json();
  if(data.authorization_url){
    window.location.href = data.authorization_url;
  } else {
    alert("Paystack init failed");
  }
}

// Premium tab: load recipes if unlocked
tabs.premium.onclick = async () => {
  switchTab("premium");
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
  const r = await fetch("/api/premium/recipes", {
    method:"POST",
    headers:{
      "Content-Type":"application/json"
    },
    body: JSON.stringify({ingredients, number:3})
  });
  const data = await r.json();
  $("#premiumList").innerHTML = "";
  if(data.recipes && data.recipes.length){
    data.recipes.forEach(rp => {
      const name = rp.name || "Untitled";
      const ingredients = Array.isArray(rp.ingredients) ? rp.ingredients : (typeof rp.ingredients === "string" ? rp.ingredients.split(",") : []);
      const instructions = rp.instructions || rp.steps || "";
      const div = document.createElement("div");
      div.className = "recipe-card";
      div.innerHTML = `<h3>${name}</h3>
                       <p><strong>Ingredients:</strong> ${ingredients.join(", ")}</p>
                       <p>${instructions}</p>`;
      $("#premiumList").appendChild(div);
    });
  } else {
    $("#premiumList").innerHTML = "No premium recipes available.";
  }
}

// set initial tab
switchTab("home");

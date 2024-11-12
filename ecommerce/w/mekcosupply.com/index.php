<?php include 'includes/header.php'; ?>

<?php include 'includes/slides.php'; ?>

<?php include 'includes/categories.php'; ?>

<?php include 'includes/footer.php'; ?>



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mekco Supply Inc.</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.10.2/css/all.css">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.10.2/css/v4-shims.css">

    <link rel="stylesheet" href="owlcarousel/owl.carousel.min.css">
    <link rel="stylesheet" href="owlcarousel/owl.theme.default.min.css">

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/slick-carousel/slick/slick.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/slick-carousel/slick/slick.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/slick-carousel/slick/slick-theme.css">

    <script defer src="js/script.js"></script>
</head>
<body>
    <header>
        <div class="topnav">
            <div class="logo-topnav"><a href="https://apprand.com/mekcosupply.com/"><img src="Mekco-Supply-logo-300px.png" alt="Mekco Supply" class="logo-topnav" width="100px"></a></div>
            <ul class="nav-links">
                <li><a href="https://maps.app.goo.gl/MWzRrqAPxbSemYLx7"><i class="fas fa-map-pin"></i></a></li>
                <li><a href="tel:905-597-4597"><i class="fas fa-phone"></i></a></li>
                <li><a href="mailto:shop@mekcosupply.com"><i class="fas fa-envelope"></i></a></li>
                <li><a href="#"><i class="fas fa-user"></i></a></li>
                <!--<li><a href="#">$110,000.00</a></li>-->
                <li><a href="#"><i class="fas fa-shopping-cart"></i></a></li>
                <li><a href="#"><i class="fas fa-sign-out-alt"></i></a></li>
            </ul>
        </div>
        <nav class="navbar">
            <!--<div class="logo"> <img src="Mekco-Supply-logo-1500px-filled.jpg" alt="Mekco Supply" class="logo"></div>
            <ul class="nav-links">
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Services</a></li>
                <li><a href="#">Contact</a></li>
            </ul>-->
            <div class="filters">
                <div class="dropdown">
                    <select>
                        <option value="filter1">CATEGORIES</option>
                        <option value="option1">PLUMBING & DRAIN</option>
                        <option value="option2">PUMPS</option>
                        <option value="option3">VALVES</option>
                        <option value="option1">WATERWORKS</option>
                        <option value="option2">TOOLS</option>
                        <option value="option3">HVAC</option>
                        <option value="option3">HYDRONICS</option>
                    </select>
                </div>
                <div class="dropdown">
                    <select>
                        <option value="filter2">MENU</option>
                        <option value="option1">ORDER STATUS <a href="#"><i class="fa-solid fa-truck-fast"></i></a></option>
                        <option value="option1">REGISTRATION</option>
                        <option value="option2">QUOTE REQUEST</option>
                        <option value="option3">ABOUT US</option>
                        <option value="option4">CONTACT US</option>
                    </select>
                </div>
            </div>

            <div class="burger">
                <div class="line1"></div>
                <div class="line2"></div>
                <div class="line3"></div>
            </div>
        </nav>
        <div class="mobile-menu">
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Services</a></li>
                <li><a href="#">Contact Us</a></li>
                <li><a href="#">Cart</a></li>
                <li>
                    <div class="search-container">
                        <input type="text" id="mobileSearch" placeholder="Search...">
                        <span class="clear-search" id="clearSearch">&#10006;</span>
                    </div>
                </li>
                <li><a href="#">Logout</a></li>
            </ul>
        </div>
        <div id="slideTab" class="slide-tab">
            <a href="javascript:void(0)" class="closebtn" onclick="closeTab()">×</a>
            <!--<p>This is a sliding tab content. This is a sliding tab content. This is a sliding tab content.</p>-->
            <!-- Replace the PHP include with appropriate HTML or JavaScript logic -->
        </div>
        <span class="openbtn" onclick="openTab()">☰ $100,00.00</span>
    </header>
</body>
</html>
<main>
    <section class="content">
        <!--<h2>Best Plumbing Supply across GTA</h2>
        <div class="handle">
            <div class="fixed-tab currency"><a href="#">100000.00</a></div>
        </div>-->

        <div class="products">

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

            <div class="product">
                <div class="info-icon">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="popup-box">
                        <p>Product description goes here. Provide detailed information about the product.</p>
                    </div>
                </div>
                <div>
                    <a href="https://apprand.com/mekcosupply.com/product.php"><img src="img/5M-BCPO145MB_result.jpg" alt="Product 1"></a>
                    <br><h3>Product 1</h3><br>
                </div>
                <div class="product-actions">
                    <input type="number" min="1" value="1" class="quantity-input">
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>

        </div>

    </section>
<!--
    <section class="about">
        <h2>About Us</h2>
        <p>We are a team of dedicated professionals committed to providing top-notch products. Our mission is to deliver high-quality solutions to our clients.</p>
    </section>

    <section class="contact">
        <h2>Contact Us</h2>
        <p>If you have any questions, feel free to reach out to us at <a href="mailto:shop@mekcosupply.com">shop@mekcosupply.com</a>.</p>
    </section>
-->
</main>
<footer>
    <div class="footer-content">
        <img src="Mekco-Supply-logo-300px.png" alt="Footer Image" class="footer-image">
        <p>&copy; <span id="current-year"></span> Mekco Supply Inc. All rights reserved.</p>
    </div>
</footer>

<script src="jquery.min.js"></script>
<script>
    // Set the current year in the footer
    document.getElementById("current-year").textContent = new Date().getFullYear();
</script>

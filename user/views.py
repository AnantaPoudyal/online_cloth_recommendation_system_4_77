import os
import django
import pandas as pd

# Initialize Django
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

#sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#user app models and forms
from user.forms import usersearchForm
from user.forms import usersearchForm
from user.forms import qtyForm, usersearchForm
from user.models import Cart, buyProduct, popoularItemByView

#viewer app create_user model
from viewer.models import create_user

from .models import Products, create_user, Cart, buyProduct
from .forms import qtyForm

from manageProducts.models import (

    BaseColour, MasterCategory, Products, SubCategory, Season, ArticleType, Gender
)



# Initialize global variables
REFINED_DATA = None
UNIVERSAL_TAG = None
NEW_REFINED_DATA = None

# Set the base directory of your project
BASE_DIR = "D:\\bca\\6th sem files\\project ii\\online_cloth_recommendation_system_4_77"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_cloth_recommendation_system_4_77.settings')

# Setup Django
django.setup()

# Paths and filenames
IMAGE_FOLDER_PATH = os.path.join(BASE_DIR, "static", "images")
STYLES_CSV_PATH = os.path.join(BASE_DIR, "static", "styles.csv")


# ========================= Helper Functions ========================= #
def load_data_from_db():
    """Load data from the database (Currently uses CSV)."""
    products = Products.objects.all().values()
    return pd.DataFrame(list(products))  # pd.read_csv(STYLES_CSV_PATH)


def load_data(image_folder_path):
    df1 = load_data_from_db()
    image_files = sorted(os.listdir(image_folder_path))
    image_ids = [int(filename.split(".")[0]) for filename in image_files]
    df_filenames = pd.DataFrame({"filename": image_files, "id": image_ids})
    return df1, df_filenames


def merge_and_clean_data(df1, df_filenames):
    """Merge datasets, clean the data, and filter for clothing-related items."""
    clothing_subcategories = set([
        'Topwear', 'Bottomwear', 'Innerwear', 'Dress', 'Apparel Set', 'Loungewear and Nightwear', 
        'Saree', 'Kurtas', 'Kurta Sets', 'Jumpsuit', 'Leggings', 'Trousers', 'Sweaters', 'Sweatshirts',
        'Tunics', 'Nightdress', 'Shirts', 'Jeans', 'Tshirts', 'Track Pants', 'Shorts', 'Skirts', 'Capris', 
        'Camisoles', 'Blazers', 'Vest', 'Salwar', 'Churidar'
    ])

    merged_data = pd.merge(df1, df_filenames, left_on='product_id', right_on="id", how="inner")
    merged_data = merged_data.dropna(subset=["baseColour_id", "season_id", "usage", "productDisplayName", "filename"])
    merged_data = merged_data.drop(columns=["Extra1", "Extra2"], errors='ignore')

    return merged_data[
        (merged_data['masterCategory_id'] == 'Apparel') & 
        (merged_data['subCategory_id'].isin(clothing_subcategories))
    ]


def create_universal_tag(refined_data):
    """Create a 'universal tag' combining key product attributes."""
    refined_data["year"] = refined_data["year"].astype(str)
    refined_data["allCategory"] = refined_data[[
        "gender_id", "masterCategory_id", "subCategory_id", "articleType_id", "season_id", "baseColour_id",
        "year", "usage", "productDisplayName"
    ]].agg(' '.join, axis=1)

    return refined_data[["allCategory"]]


def prepare_dataset(refined_data, universal_tag):
    """Prepare the final dataset with product details and the universal tag."""
    refined_data["allCategory"] = universal_tag["allCategory"]
    return refined_data[["id", "productDisplayName", "filename", "allCategory"]]


def find_similar_items(keyword, dataset, vectorizer, similarity_matrix, nth=15):
    """Find items similar to the provided keyword."""
    keyword_vector = vectorizer.transform([keyword]).toarray()
    keyword_similarity = cosine_similarity(keyword_vector, similarity_matrix).flatten()
    similar_indices = keyword_similarity.argsort()[::-1][:70]
    similar_items = dataset.iloc[similar_indices].copy()
    similar_items['similarity'] = keyword_similarity[similar_indices]
    return similar_items[:nth]


def sideBar():
    """Prepare sidebar context with filters."""
    sideBarContext = {
        'sub_categories': SubCategory.objects.all(),
        'article_types': ArticleType.objects.all(),
        'base_colours': BaseColour.objects.all(),
        'seasons': Season.objects.all(),
        'genders': Gender.objects.all(),
    }
    return sideBarContext
##################################################################################################
CATEGORY_SIZE = 50
def get_slider_images(nth):
    """Helper function to retrieve images for the slider."""
    image_files = [image for image in os.listdir(IMAGE_FOLDER_PATH) if image.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif']]
    image_files.sort()  # Ensure consistent order
    return image_files[:nth]

def get_items(nth, search):
     # Load the data from CSV and images folder
    df1, df_filenames = load_data(IMAGE_FOLDER_PATH)
    refined_data = merge_and_clean_data(df1, df_filenames)
    
    # Create the universal tag for vectorization
    universal_tag = create_universal_tag(refined_data)
    new_refined_data = prepare_dataset(refined_data, universal_tag)
  
    """Get similar items based on a search keyword."""
    keyword = search if search else ""
    
    # Vectorization and similarity matrix caching
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector = cv.fit_transform(new_refined_data["allCategory"]).toarray()
    
    similar_items = find_similar_items(keyword, new_refined_data, cv, vector, nth)
    return similar_items.to_dict(orient="records")
# Helper function for pagination
def paginate_products(request, products):
    paginator = Paginator(products, CATEGORY_SIZE)  # Show CATEGORY_SIZE products per page.
    page = request.GET.get('page')  # Get the page number from the request
    try:
        paged_products = paginator.page(page)
    except PageNotAnInteger:
        paged_products = paginator.page(1)  # If page is not an integer, show the first page
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)  # If page is out of range, show last page
    return paged_products
# Helper function for fetching user data
def get_user_from_session(request):
    username = request.session.get('username')
    try:
        user = create_user.objects.get(usernames=username)
    except create_user.DoesNotExist:
        return None
    return user

# Helper function to check if the user is logged in
def check_logged_in(request):
    if not request.session.get('logged_in', False):
        return redirect('login')
    return None
# Helper function to retrieve user
def get_user_from_session(request):
    username = request.session.get('username')
    return get_object_or_404(create_user, usernames=username)


# Fetch User Purchased Items Optimization
def fetch_user_purchased_items(user):
    # Fetch products purchased by the user using select_related to optimize database queries
    purchased_products = buyProduct.objects.filter(user_id=user).select_related('product')
    return purchased_products


# Find Similar Items Optimization
def find_similar_items_by_purchased(keyword, dataset, vectorizer, similarity_matrix):
    keyword_vector = vectorizer.transform([keyword]).toarray()
    keyword_similarity = cosine_similarity(keyword_vector, similarity_matrix).flatten()
    similar_indices = keyword_similarity.argsort()[::-1][:3]
    
    similar_items = dataset.iloc[similar_indices].copy()
    similar_items['similarity'] = keyword_similarity[similar_indices]
    return similar_items
################################################################################################   
def userHomepage(request):
    # Check if the user is logged in
    userID = request.session.get('user_id')
    userName = request.session.get('username')
    
    if not userID or not userName:
        # If the user is not logged in, redirect to the login page
        return redirect('login')  # Make sure 'login' is the correct name for your login route

    # Load and cache data only once
    global REFINED_DATA, UNIVERSAL_TAG, NEW_REFINED_DATA
    if REFINED_DATA is None:
        df1, df_filenames = load_data(IMAGE_FOLDER_PATH)
        REFINED_DATA = merge_and_clean_data(df1, df_filenames)
        UNIVERSAL_TAG = create_universal_tag(REFINED_DATA)
        NEW_REFINED_DATA = prepare_dataset(REFINED_DATA, UNIVERSAL_TAG)
    
    # Get slider images and items
    images = get_slider_images(5)
    items = get_items(5, "")
    sideBarData = sideBar()
    popular_items = popoularItemByView.objects.order_by('counter')[:15]  # Adjust the number as needed
    
    context = {
        'userSearchForm': usersearchForm,
        'userID': userID,
        'username': userName,
        'images': images,
        'items': items,
        'sideBar': sideBarData,
        'content': {'popular_items': popular_items},
    }
    return render(request, 'userHomepage.html', context)




# Pagination view for userItems
def userItems(request):
    items = get_items(55, "blue")
    paginator = Paginator(items, 10)  # Show 10 items per page.
    page = request.GET.get('page')
    
    try:
        paged_items = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        paged_items = paginator.page(1)
    
    sideData = sideBar()
    return render(request, 'userItems.html', {'userSearchForm': usersearchForm, "items": paged_items, "sideBar": sideData})

def userItemDetails(request, item_id):
    """Render details of a single item and similar items."""
    item = REFINED_DATA.loc[REFINED_DATA["product_id"] == item_id].iloc[0]
    individualItemsTag = create_universal_tag(pd.DataFrame([item])).iloc[0]
    
    # Get similar items based on the individual item
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector = cv.fit_transform(NEW_REFINED_DATA["allCategory"])
    similar_items = find_similar_items(individualItemsTag["allCategory"], NEW_REFINED_DATA, cv, vector)
    
    sideData = sideBar()
    context = {
        "item": item.to_dict(),
        "individualItemsTag": individualItemsTag["allCategory"],
        "similar_items": similar_items.to_dict(orient="records"),
    }
    return render(request, 'userItemDetail.html', {'userSearchForm': usersearchForm, "content": context, "sideBar": sideData})





# Consolidated view for product filtering
def user_products_by_filter(request, filter_name, filter_value):
    if filter_name == "season":
        filter_field = Season.objects.get(season_name=filter_value)
        products = Products.objects.filter(season=filter_field)
    elif filter_name == "subcategory":
        filter_field = SubCategory.objects.get(sub_category_name=filter_value)
        products = Products.objects.filter(subCategory=filter_field)
    elif filter_name == "articleType":
        products = Products.objects.filter(articleType=filter_value)
    elif filter_name == "baseColour":
        products = Products.objects.filter(baseColour=filter_value)
    elif filter_name == "usage":
        products = Products.objects.filter(usage=filter_value)
    elif filter_name == "gender":
        products = Products.objects.filter(gender=filter_value)
    else:
        products = Products.objects.all()  # Default: fetch all products
    
    paged_products = paginate_products(request, products)
    sideData = sideBar()  # Assuming sideBar() returns sidebar data
    return render(request, 'user_product_list.html', {'userSearchForm': usersearchForm, 'products': paged_products, "sideBar": sideData})

# Specific views
def user_products_by_season(request, season_name):
    return user_products_by_filter(request, "season", season_name)

def user_products_by_subcategory(request, sub_category_name):
    return user_products_by_filter(request, "subcategory", sub_category_name)

def user_products_by_article_type(request, articleType_name):
    return user_products_by_filter(request, "articleType", articleType_name)

def user_products_by_base_colour(request, baseColour_name):
    return user_products_by_filter(request, "baseColour", baseColour_name)

def user_products_by_usage(request, usage_name):
    return user_products_by_filter(request, "usage", usage_name)

def user_products_by_gender(request, gender_name):
    return user_products_by_filter(request, "gender", gender_name)


########################################################################





# User Account View
def userAccount(request):
    sideData = sideBar()
    if check_logged_in(request):
        return check_logged_in(request)

    user = get_user_from_session(request)
    context = {
        "username": request.session.get('username'),
        "user": user,
        "searchForm": usersearchForm(),
        "sideBar": sideData
    }
    return render(request, 'userAccountPage.html', {'userSearchForm': usersearchForm(), "content": context})

# Edit User Account View
def editUserAccount(request):
    sideData = sideBar()
    if check_logged_in(request):
        return check_logged_in(request)

    user = get_user_from_session(request)
    if user is None:
        return redirect('userAccount')

    context = {
        "user": user,
        "sideBar": sideData,
    }
    return render(request, 'editUserAccountPage.html', {'userSearchForm': usersearchForm(), "content": context})

# Update User Account View
def updateUserAccount(request):
    sideData = sideBar()
    if check_logged_in(request):
        return check_logged_in(request)

    user = get_user_from_session(request)
    if user is None:
        return redirect('userAccount')

    if request.method == 'POST':
        DOB = request.POST.get('DOB')
        address = request.POST.get('address')
        password = request.POST.get('password')

        user.DOB = DOB
        user.address = address
        if password:
            user.password = password  # In real applications, hash the password
        user.save()

        return redirect('userAccount')

    context = {
        "user": user,
        "sideBar": sideData,
    }
    return render(request, 'editUserAccountPage.html', {'userSearchForm': usersearchForm(), "content": context})
###################################################




# Add to Cart View
def add_to_cart(request, product_id):
    user = get_user_from_session(request)
    product = get_object_or_404(Products, product_id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if created:
        messages.add_message(request, messages.INFO, "Item added to cart.")
    else:
        cart_item.quantity += 1
        cart_item.save()
        messages.add_message(request, messages.INFO, "Item is already in your cart.")
    
    return redirect('userItems')

# User Cart View
def userCart(request):
    sideData = sideBar()
    if not request.session.get('logged_in', False):
        return redirect('viewerLoginpage')

    user = get_user_from_session(request)
    cart_items = Cart.objects.filter(user=user)

    context = {
        "cart_items": cart_items,
        "sideBar": sideData,
        'userSearchForm': usersearchForm,
    }
    return render(request, 'userCart.html', {'userSearchForm': usersearchForm, "content": context, "sideBar": sideData})

# Remove from Cart View
def remove_from_cart(request, product_id):
    user = get_user_from_session(request)
    cart_item = get_object_or_404(Cart, user=user, product_id=product_id)
    cart_item.delete()
    messages.add_message(request, messages.INFO, "Item removed from cart.")
    return redirect('userCart')

# Buy Product View
def buy(request, item_id):
    product = get_object_or_404(Products, product_id=item_id)
    if request.method == 'POST':
        form = qtyForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['qty']
            user = get_user_from_session(request)

            total_amount = product.price * qty
            if qty > product.quantity:
                messages.error(request, "Not enough stock available.")
                return render(request, 'buy_product.html', {"product": product, "form": form})
            else:
                product.quantity -= qty
                product.save()

                # Create purchase record
                purchase = buyProduct(
                    user=user,
                    product=product,
                    quantity=qty,
                    amt=product.price,
                    total=total_amount,
                    purchase_date=timezone.now(),
                    address=user.address,
                )
                purchase.save()

                messages.add_message(request, messages.INFO, "Purchase successful!")
                return redirect('purchase_success')

    else:
        form = qtyForm()

    return render(request, 'buy_product.html', {'userSearchForm': usersearchForm, "product": product, "form": form})

# Purchase Success View
def purchase_success(request):
    return render(request, 'purchase_success.html')

# Order History View
def order_history(request):
    user = get_user_from_session(request)
    orders = buyProduct.objects.filter(user=user).order_by('-purchase_date')

    return render(request, 'order_history.html', {'userSearchForm': usersearchForm, 'orders': orders})

# Cancel Order View
def cancel_order(request, order_id):
    if not request.session.get('logged_in', False):
        return redirect('viewerLoginpage')

    order = get_object_or_404(buyProduct, id=order_id)
    # Assuming we can cancel only if the order is not already completed
    if order.purchase_date:
        order.delete()
        messages.add_message(request, messages.INFO, "Order cancelled successfully.")
    else:
        messages.add_message(request, messages.ERROR, "Cannot cancel the order.")
    
    return redirect('order_history')



# Cancel Order Optimization
def cancel_order(request, order_id):
    if not request.session.get('logged_in', False):
        return redirect('viewerLoginpage')
    
    order = get_object_or_404(buyProduct, id=order_id, user__usernames=request.session['username'])
    productID = order.product_id

    if order.status == 'pending':
        order.status = 'canceled'
        
        # Use select_related to fetch the product and related fields in one query
        product = Products.objects.select_related('gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season').get(product_id=productID)
        product.quantity += order.quantity
        product.save()

        # Delete the order after updating product quantity
        order.delete()
        messages.success(request, 'Order has been canceled successfully.')
    else:
        messages.error(request, 'Order cannot be canceled.')
    
    return redirect('userOrder')


# User Orders Page Optimization
def order(request):
    username = request.session.get('username')
    user = get_object_or_404(create_user, usernames=username)

    # Use select_related to fetch related fields to reduce queries
    orders = buyProduct.objects.filter(user=user).select_related('product').order_by('-purchase_date')

    return render(request, 'user_order.html', {
        'userSearchForm': usersearchForm,
        'orders': orders,
        'sideBar': sideBar(),
    })


# Logout Optimization
def logout(request):
    if request.session.get('logged_in', False):
        request.session.flush()  # More efficient than deleting individual keys
    return redirect('login')

# Similar Items for Purchased Items Optimization
def find_similar_items_for_purchased_items(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(create_user, usernames=username)
    purchased_items = buyProduct.objects.filter(user=user).select_related('product')

    # Prepare the dataset for similarity search
    df1, df_filenames = load_data(IMAGE_FOLDER_PATH)
    refined_data = merge_and_clean_data(df1, df_filenames)
    universal_tag = create_universal_tag(refined_data)
    new_refined_data = prepare_dataset(refined_data, universal_tag)

    # Vectorization and similarity check
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector = cv.fit_transform(new_refined_data["allCategory"]).toarray()

    similar_items = []
    for item in purchased_items:
        keyword = item.product.productDisplayName  # Assuming productDisplayName is used for similarity search
        similar_items += find_similar_items_by_purchased(keyword, new_refined_data, cv, vector).to_dict(orient="records")

    paginator = Paginator(similar_items, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'userSimilarItem.html', {
        'sideBar': sideBar(),
        'userSearchForm': usersearchForm(),
        'content': {
            'qtyForm': qtyForm(),
            'page_obj': page_obj
        }
    })


# Popular Items View Optimization
def popular_items_view(request):
    popular_items = popoularItemByView.objects.order_by('-counter')[:15]
    return render(request, 'userPopularItem.html', {
        'sideBar': sideBar(),
        'userSearchForm': usersearchForm(),
        'content': {'popular_items': popular_items}
    })


# Searched Items Optimization
def searched_items(request):
    query = request.GET.get('search', '')
    searched_items = get_items(30, query)  # Adjust the limit as needed

    paginator = Paginator(searched_items, 10)
    page = request.GET.get('page')

    try:
        paged_items = paginator.page(page)
    except PageNotAnInteger:
        paged_items = paginator.page(1)
    except EmptyPage:
        paged_items = paginator.page(paginator.num_pages)

    return render(request, 'userSearchedItems.html', {
        'userSearchForm': usersearchForm(),
        'items': paged_items,
        'sideBar': sideBar(),
        'search_query': query,
    })


# Dashboard Optimization
def dashboard(request):
    username = request.session.get('username')
    user = create_user.objects.get(usernames=username)

    # Using aggregate for calculating total orders and total spent
    total_orders = buyProduct.objects.filter(user=user).exclude(status='canceled').count()
    cart_items_count = Cart.objects.filter(user=user).count()
    total_spent = buyProduct.objects.filter(user=user).exclude(status='canceled').aggregate(total=Sum('total'))['total'] or 0

    # Fetch recent orders
    recent_orders = buyProduct.objects.filter(user=user).order_by('-purchase_date')[:3]

    return render(request, 'userDashboard.html', {
        'userSearchForm': usersearchForm(),
        'sideBar': sideBar(),
        'total_orders': total_orders,
        'cart_items_count': cart_items_count,
        'total_spent': total_spent,
        'recent_orders': recent_orders
    })

import os
import django
import pandas as pd

from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from viewer.forms import searchForm, viewerRegistrationForm
from viewer.models import create_user
from manageProducts.models import BaseColour, MasterCategory, Products, SubCategory, Season, ArticleType, Gender



from .forms import LoginForm, PasswordResetForm,viewerRegistrationForm,searchForm



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
    return pd.read_csv(STYLES_CSV_PATH)

def load_data(styles_csv_path, image_folder_path):
    """Load and prepare data from the database and image folder."""
    df1 = load_data_from_db()
    image_files = sorted(os.listdir(image_folder_path))
    image_ids = [int(filename.split(".")[0]) for filename in image_files]
    df_filenames = pd.DataFrame({"filename": image_files, "id": image_ids})
    return df1, df_filenames

def merge_and_clean_data(df1, df_filenames):
    """Merge datasets, clean the data, and filter for clothing-related items."""
    clothing_subcategories = [
        'Topwear', 'Bottomwear', 'Innerwear', 'Dress', 'Apparel Set', 'Loungewear and Nightwear', 
        'Saree', 'Kurtas', 'Kurta Sets', 'Jumpsuit', 'Leggings', 'Trousers', 'Sweaters', 'Sweatshirts', 
        'Tunics', 'Nightdress', 'Shirts', 'Jeans', 'Tshirts', 'Track Pants', 'Shorts', 'Skirts', 
        'Capris', 'Camisoles', 'Blazers', 'Vest', 'Salwar', 'Churidar'
    ]

    # Merge and clean data
    merged_data = pd.merge(df1, df_filenames, on="id", how="inner")
    merged_data.dropna(subset=["baseColour", "season", "usage", "productDisplayName", "filename"], inplace=True)
    refined_data = merged_data.drop(columns=["Extra1", "Extra2"], errors='ignore')

    return refined_data[(refined_data['masterCategory'] == 'Apparel') & 
                         (refined_data['subCategory'].isin(clothing_subcategories))]


def create_universal_tag(refined_data):
    """Create a universal tag for each product combining various attributes."""
    refined_data["year"] = refined_data["year"].astype(str)
    refined_data["allCategory"] = refined_data.apply(lambda row: ' '.join(row[["gender", "masterCategory", "subCategory", "articleType", 
                                                                              "baseColour", "season", "year", "usage", "productDisplayName"]].astype(str)), axis=1)
    return refined_data[["allCategory"]]

def prepare_dataset(refined_data, universal_tag):
    """Prepare the final dataset combining refined data and the universal tag."""
    dataset = refined_data[["id", "productDisplayName", "filename"]].copy()
    dataset["allCategory"] = universal_tag["allCategory"]
    return dataset

def find_similar_items(keyword, dataset, vectorizer, similarity_matrix, nth=15):
    """Find the most similar items based on cosine similarity."""
    keyword_vector = vectorizer.transform([keyword]).toarray()
    keyword_similarity = cosine_similarity(keyword_vector, similarity_matrix).flatten()
    similar_indices = keyword_similarity.argsort()[::-1][:70]  # Get top 70 similar items
    similar_items = dataset.iloc[similar_indices].copy()
    similar_items['similarity'] = keyword_similarity[similar_indices]
    return similar_items.head(nth)  # Return top 'nth' similar items

def sideBar():
    sub_categories = SubCategory.objects.all()
    article_types = ArticleType.objects.all()
    base_colours = BaseColour.objects.all()
    seasons = Season.objects.all()
    genders = Gender.objects.all()
    sideBarContext = {
        'sub_categories': sub_categories,
        'article_types': article_types,
        'base_colours': base_colours,
        'seasons': seasons,
        'genders': genders,
    } 
    return sideBarContext
# View for the homepage
# View for the homepage
def homepage(request):
    # Fetch images for the slider (fetch only required number)
    images = get_slider_images(5)
    
    # Get the items for the homepage
    items = get_homepage_item()

    # Get the sidebar data
    sideBarData = sideBar()

    # Render the homepage template
    return render(request, "viewerHomepage.html", {
        "images": images,
        "items": items,
        "searchForm":searchForm(),
       "sideBar": sideBar()
    })



def get_homepage_item():
    """Fetch a set of items for the homepage."""
    return get_items(10, "")

# View for displaying items
def items(request):
    """Display items with pagination."""
    items = get_items(100, "")  # Adjust 'nth' value to fetch more items
    sideData = sideBar()

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, 25)  # Show 25 items per page
    paginated_items = paginator.get_page(page_number)

    # Context for rendering the template
    context = {
        "items": paginated_items,
        
    }

    # Render the page
    return render(request, "viewerItempage.html", {"content": context,"sideBar": sideData,"searchForm": searchForm(),
        })

from django.core.paginator import Paginator

def searched_items(request):
    sideData = sideBar()
    
    # Initialize search form
    form = searchForm(request.GET)
    
    if form.is_valid():
        # Get the search keyword from the form
        searched_keyword = form.cleaned_data.get('search')

        # Call get_items with the search keyword
        items = get_items(25, searched_keyword)

        # Pagination logic
        paginator = Paginator(items, 10)  # Show 10 items per page
        page_number = request.GET.get('page')
        paged_items = paginator.get_page(page_number)

        context = {
            "items": paged_items,
            "searchForm": form,  # Use the same form instance
        }
        
        # Render the template with the filtered and paginated items
        return render(request, "viewerItempage.html", {
            "content": context,
            "sideBar": sideData,
            "searchForm": form,  # Ensure you pass the form instance here
        })
    
    # If the form is not valid or no search query is entered, redirect to the default items view
    return redirect('items')



def getKeyword(request):
    return request.GET.get("search", "")

def itemDetails(request, item_id):
    sideData = sideBar()
    
    # Load data
    df1, df_filenames = load_data(STYLES_CSV_PATH, IMAGE_FOLDER_PATH)
    refined_data = merge_and_clean_data(df1, df_filenames)
    
    # Fetch the specific item by ID
    item = refined_data.loc[refined_data["id"] == item_id].iloc[0]
    individualItemsTag = create_universal_tag(pd.DataFrame([item])).iloc[0]
    
    # Prepare the dataset and vectorize
    universal_tag = create_universal_tag(refined_data)
    new_refined_data = prepare_dataset(refined_data, universal_tag)
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector = cv.fit_transform(new_refined_data["allCategory"])
    
    # Get similar items based on the item's category
    item_allCategory = individualItemsTag["allCategory"]
    similar_items = find_similar_items(item_allCategory, new_refined_data, cv, vector)
    
    # Prepare context for the template
    context = {
        "item": item.to_dict(),
        "individualItemsTag": item_allCategory,
        "searchForm": searchForm(),  # You can use a single instance here if you want
        "similar_items": similar_items.to_dict(orient="records"),
    }

    # Render the item details page with the context
    return render(request, "viewerItemDetails.html", {"content": context, "sideBar": sideData})




CATEGORY_SIZE = 50

from django.core.paginator import Paginator

def get_filtered_products(request, filter_name, filter_value):
    if filter_name == "season":
        filter_field = Season.objects.get(season_name=filter_value)
        products = Products.objects.filter(season=filter_field)
    elif filter_name == "subcategory":
        filter_field = SubCategory.objects.get(sub_category_name=filter_value)
        products = Products.objects.filter(subCategory=filter_field)
    elif filter_name == "articleType":
        filter_field = ArticleType.objects.get(articleType_name=filter_value)
        products = Products.objects.filter(articleType=filter_field)
    elif filter_name == "baseColour":
        filter_field = BaseColour.objects.get(baseColour_name=filter_value)
        products = Products.objects.filter(baseColour=filter_field)
    elif filter_name == "usage":
        products = Products.objects.filter(usage=filter_value)
    elif filter_name == "gender":
        filter_field = Gender.objects.get(gender_name=filter_value)
        products = Products.objects.filter(gender=filter_field)
    else:
        products = Products.objects.all()  # Default: fetch all products
    
    return products

def products_by_filter(request, filter_name, filter_value):
    products = get_filtered_products(request, filter_name, filter_value)
    
    # Pagination logic
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)
    
    sideData = sideBar()  # Assuming sideBar() returns sidebar data
    content = {'products': paged_products, 'sideBar': sideData}
    
    return render(request, 'product_list.html', {'content': content, 'sideBar': sideData})

# Now, you can simplify your individual views like this:

def products_by_subcategory(request, sub_category_name):
    return products_by_filter(request, 'subcategory', sub_category_name)

def products_by_article_type(request, articleType_name):
    return products_by_filter(request, 'articleType', articleType_name)

def products_by_base_colour(request, baseColour_name):
    return products_by_filter(request, 'baseColour', baseColour_name)

def products_by_season(request, season_name):
    return products_by_filter(request, 'season', season_name)

def products_by_gender(request, gender_name):
    return products_by_filter(request, 'gender', gender_name)

# View for login page
# views.py




def custom_404_view(request, exception):
    return render(request, 'viewer404error.html', status=404)



def login(request):
    sideData = sideBar()
    
    # If user is already logged in, redirect to homepage
    if request.session.get('logged_in', False):
        return redirect('userHomepage')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usernames']
            password = form.cleaned_data['password']
            
            try:
                # Retrieve the user by username
                user = create_user.objects.get(usernames=username)
                
                # Check if the entered password matches the stored hashed password
                if check_password(password, user.password):
                    # Set session or other login actions
                    request.session['user_id'] = user.id  # Example session setting
                    request.session['logged_in'] = True
                    request.session['username'] = username
                    messages.success(request, 'Login successful')
                    return redirect('userHomepage')  # Redirect to a desired page after login
                else:
                    messages.error(request, 'Invalid username or password')
            except create_user.DoesNotExist:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please fix the errors below')
    else:
        form = LoginForm()

    return render(request, 'viewerLoginpage.html', {'form': form, 'sideBar': sideData})




# View for registration page

def register(request):
    sideData = sideBar()  # Assuming this function retrieves sidebar data
    
    # If the user is already logged in, redirect to homepage
    if request.session.get('logged_in', False):
        return redirect('userHomepage')
    
    form = viewerRegistrationForm()

    if request.method == 'POST':
        form = viewerRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usernames']
            password = form.cleaned_data['password']
            dob = form.cleaned_data['DOB']
            address = form.cleaned_data['address']
            
            # Check if the username already exists
            if create_user.objects.filter(usernames=username).exists():
                messages.error(request, 'Username already exists. Please choose another one.')
                return render(request, 'viewerRegistrationpage.html', {"form": form, "sideBar": sideData})

            # Hash the password
            hashed_password = make_password(password)

            # Create the new user
            create_user.objects.create(
                usernames=username,
                password=hashed_password,
                DOB=dob,
                address=address
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')

    return render(request, 'viewerRegistrationpage.html', {"form": form, "sideBar": sideData})

def registration_success(request):
    return render(request, 'registration_success.html')

def forgot_password(request):
    sideData = sideBar()

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('usernames')
            new_password = form.cleaned_data.get('new_password')

            try:
                # Fetch user by the provided username
                user = create_user.objects.get(usernames=username)
                
                if new_password:
                    # Set the new password and save it
                    user.password = make_password(new_password)
                    user.save()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('password_change_successful')  # Redirect to success page after password reset
                
                # If only the username is provided (initial step)
                # Ideally, send an email or confirmation (depending on the flow)
                messages.info(request, 'Username recognized. Please enter a new password.')
                return redirect('forgot_password')
            
            except create_user.DoesNotExist:
                messages.error(request, 'User not found')

    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password.html', {'form': form, 'sideBar': sideData})



# Password change successful view
def password_change_successful(request):
    sideData = sideBar()
    return render(request, 'password_change_successful.html', {'sideBar': sideData})

# View for displaying items with filtering
def get_items(nth, search):
    # Load the data from CSV and images folder
    df1, df_filenames = load_data(STYLES_CSV_PATH, IMAGE_FOLDER_PATH)
    refined_data = merge_and_clean_data(df1, df_filenames)
    
    # Create the universal tag for vectorization
    universal_tag = create_universal_tag(refined_data)
    new_refined_data = prepare_dataset(refined_data, universal_tag)

    # Apply search query (if provided)
    keyword = search if search else ""

    # Vectorize the tags and find similar items
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vector = cv.fit_transform(new_refined_data["allCategory"]).toarray()

    # Find similar items based on the search keyword and the nth limit
    similar_items = find_similar_items(keyword, new_refined_data, cv, vector, nth)
    
    # Limit the number of items to the value of 'nth'
    limited_items = similar_items[:nth].to_dict(orient="records")  # Convert to a list of dictionaries
    
    return limited_items

# View for the image slider
def get_slider_images(nth):
    """Helper function to retrieve images for the slider."""
    image_files = os.listdir(IMAGE_FOLDER_PATH)
    image_files.sort()  # Ensure consistent order
    
    # Optionally filter only image files
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    images = [image for image in image_files if image.split('.')[-1].lower() in allowed_extensions]

    return images[:nth]

# View for the slider page (if needed separately)
def slider_view(request):
    # Default value for 'nth' (can be dynamic, for example, 5 images at a time)
    nth = 5  # You can modify this if you'd like to fetch a different number of images

    # Retrieve the images for the slider
    images = get_slider_images(nth)

    # Optionally handle search form or other logic
    search_form = searchForm(request.GET or None)

    # If the search form is valid, you can handle the search logic here
    if search_form.is_valid():
        search = search_form.cleaned_data['search']
        # Process search if needed or pass to context
        # You could call get_items here and pass the search results as well

    return render(request, 'slider.html', {'images': images, 'searchForm': search_form})

import os
import streamlit as st
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TripMind",
    page_icon="✈️",
    layout="wide",
)
BACKEND_URL = os.getenv(
    "https://tripmind-backend.vercel.app/",
    "http://127.0.0.1:8000",
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_transport_icon(mode):
    mode = str(mode).lower()

    if mode == "flight":
        return "✈️"
    if mode == "train":
        return "🚆"
    if mode == "bus":
        return "🚌"
    if mode == "car":
        return "🚗"

    return "🚉"


def display_transport_card(option, selected):
    mode = option.get("mode", "Transport")
    icon = get_transport_icon(mode)

    border = "#4CAF50" if selected else "#444"
    background = "#102a19" if selected else "#111"

    st.markdown(
        f"""
        <div style="
            border: 2px solid {border};
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 10px;
            background-color: {background};
            min-height: 190px;
        ">
            <h3>{icon} {mode}</h3>
            <p><strong>{option.get('provider', 'Unknown provider')}</strong></p>
            <p>
                📍 {option.get('departure', '')}
                →
                {option.get('arrival', '')}
            </p>
            <p>⏱️ {option.get('duration', '')}</p>
            <h3>
                💰 ₹{option.get('estimated_cost', 0):,.0f}
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_accommodation_card(option, selected):
    border = "#4CAF50" if selected else "#444"
    background = "#102a19" if selected else "#111"

    amenities = option.get("amenities", [])

    amenities_text = (
        ", ".join(amenities)
        if amenities
        else "Amenities not specified"
    )

    rating = option.get("rating")

    st.markdown(
        f"""
        <div style="
            border: 2px solid {border};
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 10px;
            background-color: {background};
            min-height: 230px;
        ">
            <h3>🏨 {option.get('name', 'Accommodation')}</h3>

            <p>
                📍 {option.get('location', 'Location not specified')}
            </p>

            <p>
                ⭐ {rating if rating is not None else 'N/A'}
            </p>

            <p>
                💰 ₹{option.get('price_per_night', 0):,.0f}/night
            </p>

            <p>
                🧾 Total: ₹{option.get('total_cost', 0):,.0f}
            </p>

            <p>
                🛎️ {amenities_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

st.title("✈️ TripMind")

st.subheader("Multi-Agent AI Travel Planner")

st.write(
    "Plan your trip with AI-powered weather, transport, "
    "accommodation, restaurant, packing, and itinerary assistance."
)


# ============================================================
# TRIP INPUT FORM
# ============================================================

st.divider()

st.header("🌍 Plan Your Trip")

col1, col2 = st.columns(2)

with col1:

    source = st.text_input(
        "Starting Location",
        placeholder="e.g. Kolkata",
    )

    destination = st.text_input(
        "Destination",
        placeholder="e.g. Goa",
    )

    start_date = st.date_input(
        "Start Date",
    )

    travelers = st.number_input(
        "Number of Travelers",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
    )

    budget = st.number_input(
        "Budget (INR)",
        min_value=0.0,
        value=50000.0,
        step=5000.0,
    )


with col2:

    end_date = st.date_input(
        "End Date",
    )

    accommodation_type = st.selectbox(
        "Accommodation",
        [
            "budget",
            "comfortable",
            "luxury",
        ],
        index=1,
    )

    transport_preference = st.selectbox(
        "Transport Preference",
        [
            "any",
            "flight",
            "train",
            "bus",
            "car",
        ],
    )

    travel_pace = st.selectbox(
        "Travel Pace",
        [
            "relaxed",
            "balanced",
            "packed",
        ],
        index=1,
    )


st.subheader("🎯 Interests")

interests = st.multiselect(
    "What are you interested in?",
    [
        "beaches",
        "history",
        "food",
        "nightlife",
        "nature",
        "adventure",
        "shopping",
        "culture",
        "wellness",
    ],
    default=["beaches", "food"],
)


st.subheader("🍽️ Food Preferences")

food_preferences = st.multiselect(
    "Food preferences",
    [
        "seafood",
        "vegetarian",
        "vegan",
        "street food",
        "local cuisine",
        "fine dining",
    ],
)


# ============================================================
# CREATE TRIP
# ============================================================

st.divider()

if st.button(
    "🚀 Create My Trip Plan",
    type="primary",
    use_container_width=True,
):

    if not source.strip():

        st.error("Please enter a starting location.")

    elif not destination.strip():

        st.error("Please enter a destination.")

    elif end_date < start_date:

        st.error("End date cannot be before the start date.")

    else:

        payload = {
            "source": source,
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "travelers": travelers,
            "budget": budget,
            "currency": "INR",
            "preferences": {
                "interests": interests,
                "accommodation_type": accommodation_type,
                "transport_preference": transport_preference,
                "food_preferences": food_preferences,
                "travel_pace": travel_pace,
            },
        }

        with st.spinner(
            "🤖 TripMind agents are planning your trip..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/trip/plan",
                    json=payload,
                    timeout=180,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state["trip_id"] = result["trip_id"]
                    st.session_state["trip"] = result["trip"]

                    # Clear previous selections/results
                    st.session_state.pop(
                        "selected_options",
                        None,
                    )

                    st.session_state.pop(
                        "final_result",
                        None,
                    )

                    st.success(
                        "🎉 Trip plan created successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Backend error ({response.status_code}): "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to the TripMind backend. "
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ The trip planning request timed out. "
                    "The AI agents may still be processing."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# TRIP OPTIONS
# ============================================================

if "trip" in st.session_state:

    trip = st.session_state["trip"]

    st.divider()

    st.header("🚆 Transport Options")


    # ========================================================
    # OUTBOUND TRANSPORT
    # ========================================================

    st.subheader("🛫 Outbound Journey")

    outbound_options = trip.get(
        "outbound_transport_options",
        [],
    )

    if outbound_options:

        outbound_labels = [
            (
                f"{option.get('mode', 'Transport')} • "
                f"{option.get('provider', 'Unknown')} • "
                f"₹{option.get('estimated_cost', 0):,.0f}"
            )
            for option in outbound_options
        ]

        selected_outbound = st.radio(
            "Choose your outbound journey",
            options=range(len(outbound_options)),
            format_func=lambda index: outbound_labels[index],
            key="selected_outbound",
        )

        outbound_columns = st.columns(
            len(outbound_options)
        )

        for index, option in enumerate(
            outbound_options
        ):

            with outbound_columns[index]:

                display_transport_card(
                    option,
                    index == selected_outbound,
                )

    else:

        st.info(
            "No outbound transport options available."
        )


    # ========================================================
    # RETURN TRANSPORT
    # ========================================================

    st.subheader("🛬 Return Journey")

    return_options = trip.get(
        "return_transport_options",
        [],
    )

    if return_options:

        return_labels = [
            (
                f"{option.get('mode', 'Transport')} • "
                f"{option.get('provider', 'Unknown')} • "
                f"₹{option.get('estimated_cost', 0):,.0f}"
            )
            for option in return_options
        ]

        selected_return = st.radio(
            "Choose your return journey",
            options=range(len(return_options)),
            format_func=lambda index: return_labels[index],
            key="selected_return",
        )

        return_columns = st.columns(
            len(return_options)
        )

        for index, option in enumerate(
            return_options
        ):

            with return_columns[index]:

                display_transport_card(
                    option,
                    index == selected_return,
                )

    else:

        st.info(
            "No return transport options available."
        )


    # ========================================================
    # ACCOMMODATION
    # ========================================================

    st.divider()

    st.header("🏨 Accommodation")

    accommodation_options = trip.get(
        "accommodation_options",
        [],
    )

    if accommodation_options:

        accommodation_labels = [
            (
                f"{option.get('name', 'Accommodation')} • "
                f"₹{option.get('price_per_night', 0):,.0f}/night"
            )
            for option in accommodation_options
        ]

        selected_accommodation = st.radio(
            "Choose your accommodation",
            options=range(len(accommodation_options)),
            format_func=lambda index: (
                accommodation_labels[index]
            ),
            key="selected_accommodation",
        )

        accommodation_columns = st.columns(
            len(accommodation_options)
        )

        for index, option in enumerate(
            accommodation_options
        ):

            with accommodation_columns[index]:

                display_accommodation_card(
                    option,
                    index == selected_accommodation,
                )

    else:

        st.info(
            "No accommodation options available."
        )


    # ========================================================
    # ACTIVITIES
    # ========================================================

    st.divider()

    st.header("🎯 Activities")

    activities = trip.get(
        "recommendations",
        {},
    ).get(
        "activities",
        [],
    )

    selected_activities = []

    if activities:

        activity_columns = st.columns(
            len(activities)
        )

        for index, activity in enumerate(
            activities
        ):

            with activity_columns[index]:

                st.markdown(
                    f"### 🎯 {activity.get('name', 'Activity')}"
                )

                st.write(
                    f"📍 {activity.get('location', 'Location not specified')}"
                )

                st.write(
                    f"🏷️ {activity.get('category', 'Activity')}"
                )

                st.write(
                    f"⏱️ {activity.get('duration', 'Duration not specified')}"
                )

                st.write(
                    f"💰 ₹{activity.get('estimated_cost', 0):,.0f}/person"
                )

                st.write(
                    activity.get(
                        "description",
                        "",
                    )
                )

                if st.checkbox(
                    "Select this activity",
                    key=f"activity_{index}",
                ):

                    selected_activities.append(
                        activity
                    )

    else:

        st.info(
            "No activities available."
        )


    # ========================================================
    # ATTRACTIONS
    # ========================================================

    st.divider()

    st.header("🏛️ Attractions")

    attractions = trip.get(
        "recommendations",
        {},
    ).get(
        "attractions",
        [],
    )

    selected_attractions = []

    if attractions:

        attraction_columns = st.columns(
            len(attractions)
        )

        for index, attraction in enumerate(
            attractions
        ):

            with attraction_columns[index]:

                st.markdown(
                    f"### 🏛️ {attraction.get('name', 'Attraction')}"
                )

                st.write(
                    f"📍 {attraction.get('location', 'Location not specified')}"
                )

                st.write(
                    f"🏷️ {attraction.get('category', 'Attraction')}"
                )

                st.write(
                    f"⏱️ {attraction.get('duration', 'Duration not specified')}"
                )

                st.write(
                    f"💰 ₹{attraction.get('estimated_cost', 0):,.0f}/person"
                )

                st.write(
                    f"🕐 {attraction.get('opening_hours', 'Hours not specified')}"
                )

                st.write(
                    attraction.get(
                        "description",
                        "",
                    )
                )

                if st.checkbox(
                    "Select this attraction",
                    key=f"attraction_{index}",
                ):

                    selected_attractions.append(
                        attraction
                    )

    else:

        st.info(
            "No attractions available."
        )


    # ========================================================
    # RESTAURANTS
    # ========================================================

    st.divider()

    st.header("🍽️ Restaurants")

    restaurants = trip.get(
        "recommendations",
        {},
    ).get(
        "restaurants",
        [],
    )

    selected_restaurants = []

    if restaurants:

        restaurant_columns = st.columns(
            len(restaurants)
        )

        for index, restaurant in enumerate(
            restaurants
        ):

            with restaurant_columns[index]:

                st.markdown(
                    f"### 🍽️ {restaurant.get('name', 'Restaurant')}"
                )

                st.write(
                    f"📍 {restaurant.get('location', 'Location not specified')}"
                )

                st.write(
                    f"🍴 {restaurant.get('cuisine', 'Cuisine not specified')}"
                )

                st.write(
                    f"💵 {restaurant.get('price_range', 'Price range not specified')}"
                )

                st.write(
                    f"💰 ₹{restaurant.get('estimated_cost', 0):,.0f}/person"
                )

                if st.checkbox(
                    "Select this restaurant",
                    key=f"restaurant_{index}",
                ):

                    selected_restaurants.append(
                        restaurant
                    )


    else:

        st.info(
            "No restaurants available."
        )


    # ========================================================
    # REVIEW
    # ========================================================

    st.divider()

    st.header("🧳 Review Your Trip")

    st.subheader("🚆 Transport")

    if outbound_options:

        outbound_choice = outbound_options[
            st.session_state.get(
                "selected_outbound",
                0,
            )
        ]

        st.write(
            f"🛫 **Outbound:** "
            f"{outbound_choice.get('mode')} — "
            f"{outbound_choice.get('provider')} — "
            f"₹{outbound_choice.get('estimated_cost', 0):,.0f}"
        )

    if return_options:

        return_choice = return_options[
            st.session_state.get(
                "selected_return",
                0,
            )
        ]

        st.write(
            f"🛬 **Return:** "
            f"{return_choice.get('mode')} — "
            f"{return_choice.get('provider')} — "
            f"₹{return_choice.get('estimated_cost', 0):,.0f}"
        )


    st.subheader("🏨 Accommodation")

    if accommodation_options:

        accommodation_choice = accommodation_options[
            st.session_state.get(
                "selected_accommodation",
                0,
            )
        ]

        st.write(
            f"🏨 **{accommodation_choice.get('name')}** — "
            f"₹{accommodation_choice.get('price_per_night', 0):,.0f}/night"
        )

        st.write(
            f"Total: "
            f"₹{accommodation_choice.get('total_cost', 0):,.0f}"
        )


    st.subheader("🎯 Activities")

    if selected_activities:

        for activity in selected_activities:

            st.write(
                f"• {activity.get('name')} — "
                f"₹{activity.get('estimated_cost', 0):,.0f}/person"
            )

    else:

        st.caption(
            "No activities selected."
        )


    st.subheader("🏛️ Attractions")

    if selected_attractions:

        for attraction in selected_attractions:

            st.write(
                f"• {attraction.get('name')} — "
                f"₹{attraction.get('estimated_cost', 0):,.0f}/person"
            )

    else:

        st.caption(
            "No attractions selected."
        )


    st.subheader("🍽️ Restaurants")

    if selected_restaurants:

        for restaurant in selected_restaurants:

            st.write(
                f"• {restaurant.get('name')} — "
                f"₹{restaurant.get('estimated_cost', 0):,.0f}/person"
            )

    else:

        st.caption(
            "No restaurants selected."
        )


    # ========================================================
    # CONFIRM SELECTIONS
    # ========================================================

    st.divider()

    if st.button(
        "✅ Confirm My Selections",
        type="primary",
        use_container_width=True,
    ):

        selection_payload = {
            "trip_id": st.session_state["trip_id"],
            "outbound_transport": outbound_options[
                st.session_state.get(
                    "selected_outbound",
                    0,
                )
            ],
            "return_transport": return_options[
                st.session_state.get(
                    "selected_return",
                    0,
                )
            ],
            "accommodation": accommodation_options[
                st.session_state.get(
                    "selected_accommodation",
                    0,
                )
            ],
            "activities": selected_activities,
            "attractions": selected_attractions,
            "restaurants": selected_restaurants,
        }

        with st.spinner(
            "💾 Saving your selections..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/trip/select",
                    json=selection_payload,
                    timeout=60,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state[
                        "selected_options"
                    ] = result[
                        "selected_options"
                    ]

                    st.success(
                        "🎉 Your trip selections have been saved!"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Backend error ({response.status_code}): "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to the TripMind backend. "
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ Selection request timed out."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# FINALIZE TRIP
# ============================================================

if "selected_options" in st.session_state:

    st.divider()

    st.header("✨ Finalize Your Trip")

    st.write(
        "Your selections have been saved. "
        "Now let TripMind generate your final travel plan."
    )

    if st.button(
        "🚀 Generate My Final Trip Plan",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "🤖 Generating packing list, itinerary, and budget..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/api/trip/finalize",
                    params={
                        "trip_id": st.session_state["trip_id"],
                    },
                    timeout=180,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state[
                        "final_result"
                    ] = result

                    st.success(
                        "🎉 Your final trip plan is ready!"
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Backend error ({response.status_code}): "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Could not connect to the TripMind backend. "
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏱️ Final trip generation timed out."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# FINAL TRIP RESULTS
# ============================================================
if "final_result" in st.session_state:
    st.stop()

final_result = st.session_state.get("final_result")  
if final_result:

    st.divider()

    st.header("🎉 Your Final Trip Plan")


    # ========================================================
    # PACKING LIST
    # ========================================================

    st.subheader("🧳 Packing List")

    packing_list = final_result.get(
        "packing_list",
        [],
    )

    if packing_list:

        packing_columns = st.columns(2)

        for index, item in enumerate(
            packing_list
        ):

            with packing_columns[index % 2]:

                st.checkbox(
                    item,
                    key=f"packing_{index}",
                )

    else:

        st.info(
            "No packing items were generated."
        )


    # ========================================================
    # ITINERARY
    # ========================================================


    st.subheader("🗓️ Itinerary")

    itinerary = final_result.get("final_itinerary")

    if itinerary:

        days = itinerary.get("days", [])

        for day in days:

            st.markdown(
            f"### 📅 {day.get('date', 'Date')}"
            )

            weather = day.get("weather", {})

            if weather:
                st.markdown(
                    f"🌤️ **Weather:** "
                    f"{weather.get('temperature_c', 'N/A')}°C — "
                    f"{weather.get('condition', 'N/A')} "
                    f"(Rain probability: "
                    f"{weather.get('rain_probability', 'N/A')}%)"
                )

            st.markdown("---")

            morning = day.get("morning", {})

            if morning.get("name") != "No additional activity selected":
                st.markdown(
                    f"🌅 **Morning — {morning.get('name', '')}**  \n"
                    f"📍 {morning.get('location', '')}  \n"
                    f"⏱️ {morning.get('duration', '')}"
                )
            else:
                st.markdown("🌅 **Morning:** Free time")

            afternoon = day.get("afternoon", {})

            if afternoon.get("name") != "No additional attraction selected":
                st.markdown(
                    f"🏛️ **Afternoon — {afternoon.get('name', '')}**  \n"
                    f"📍 {afternoon.get('location', '')}  \n"
                    f"⏱️ {afternoon.get('duration', '')}"
                )
            else:
                st.markdown("🏛️ **Afternoon:** Free time")

            evening = day.get("evening", {})

            if evening.get("name") != "No restaurant selected":
                st.markdown(
                    f"🍽️ **Evening — {evening.get('name', '')}**  \n"
                    f"📍 {evening.get('location', '')}  \n"
                    f"🍴 {evening.get('cuisine', '')}"
                )
            else:
                st.markdown("🍽️ **Evening:** Free time")

            st.divider()

    else:

        st.info("No itinerary was generated.")



    # ========================================================
    # BUDGET
    # ========================================================

    st.subheader("💰 Budget Summary")

    budget_summary = final_result.get(
        "budget_summary"
    )

    if budget_summary:

        currency = budget_summary.get(
            "currency",
            "INR",
        )

        budget = budget_summary.get(
            "budget",
            0,
        )

        estimated_total = budget_summary.get(
            "estimated_total",
            0,
        )

        remaining_budget = budget_summary.get(
            "remaining_budget",
            0,
        )

        breakdown = budget_summary.get(
            "breakdown",
            {},
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Budget",
                f"{currency} {budget:,.0f}",
            )

        with col2:

            st.metric(
                "Estimated Cost",
                f"{currency} {estimated_total:,.0f}",
            )

        with col3:

            st.metric(
                "Remaining",
                f"{currency} {remaining_budget:,.0f}",
            )


        st.write("### Cost Breakdown")

        st.write(
            f"🚆 Transport: "
            f"{currency} "
            f"{breakdown.get('transport', 0):,.0f}"
        )

        st.write(
            f"🏨 Accommodation: "
            f"{currency} "
            f"{breakdown.get('accommodation', 0):,.0f}"
        )

        st.write(
            f"🎯 Activities: "
            f"{currency} "
            f"{breakdown.get('activities', 0):,.0f}"
        )

        st.write(
            f"🏛️ Attractions: "
            f"{currency} "
            f"{breakdown.get('attractions', 0):,.0f}"
        )

        st.write(
            f"🍽️ Restaurants: "
            f"{currency} "
            f"{breakdown.get('restaurants', 0):,.0f}"
        )


        if budget_summary.get(
            "within_budget"
        ):

            st.success(
                "✅ Your estimated trip cost is within budget."
            )

        else:

            st.warning(
                "⚠️ Your estimated trip cost exceeds the selected budget."
            )

    else:

        st.info(
            "No budget summary was generated."
        )
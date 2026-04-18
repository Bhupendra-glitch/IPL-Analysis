import streamlit as st
import pandas as pd
import io
from datetime import datetime

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
except ImportError:
    RandomForestClassifier = None
    train_test_split = None
    accuracy_score = None

from utils import load_data, get_teams

st.title("📥 Export Reports & Analysis")

matches, deliveries = load_data()
teams = get_teams(matches)

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📊 Team Analysis", "🎯 Match Prediction", "📤 Export Options"])

# Tab 1: Team Analysis
with tab1:
    st.header("🏏 Team Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Select Team 1", teams, key="team1")

    with col2:
        team2 = st.selectbox("Select Team 2", teams, key="team2")

    if team1 and team2:
        # Team 1 Analysis
        team1_matches = matches[(matches['team1'] == team1) | (matches['team2'] == team1)]
        team1_wins = len(team1_matches[team1_matches['winner'] == team1])
        team1_win_rate = (team1_wins / len(team1_matches)) * 100 if len(team1_matches) > 0 else 0

        # Team 2 Analysis
        team2_matches = matches[(matches['team1'] == team2) | (matches['team2'] == team2)]
        team2_wins = len(team2_matches[team2_matches['winner'] == team2])
        team2_win_rate = (team2_wins / len(team2_matches)) * 100 if len(team2_matches) > 0 else 0

        # Head-to-Head Analysis
        h2h_matches = matches[((matches['team1'] == team1) & (matches['team2'] == team2)) |
                             ((matches['team1'] == team2) & (matches['team2'] == team1))]
        team1_h2h_wins = len(h2h_matches[h2h_matches['winner'] == team1])
        team2_h2h_wins = len(h2h_matches[h2h_matches['winner'] == team2])

        st.subheader(f"📈 {team1} vs {team2} Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(f"{team1} Win Rate", f"{team1_win_rate:.1f}%", f"{team1_wins}/{len(team1_matches)} matches")
            st.metric(f"{team2} Win Rate", f"{team2_win_rate:.1f}%", f"{team2_wins}/{len(team2_matches)} matches")

        with col2:
            st.metric("Head-to-Head Matches", len(h2h_matches))
            st.metric(f"{team1} H2H Wins", team1_h2h_wins)
            st.metric(f"{team2} H2H Wins", team2_h2h_wins)

        with col3:
            # Venue analysis for these teams
            venue_matches = h2h_matches.dropna(subset=['venue'])
            if len(venue_matches) > 0:
                top_venue = venue_matches['venue'].mode().iloc[0] if len(venue_matches['venue'].mode()) > 0 else "N/A"
                st.metric("Common Venue", top_venue[:25] + "..." if len(top_venue) > 25 else top_venue)

        # Store analysis results for export
        st.session_state.team_analysis = {
            'team1': team1,
            'team2': team2,
            'team1_win_rate': team1_win_rate,
            'team2_win_rate': team2_win_rate,
            'h2h_matches': len(h2h_matches),
            'team1_h2h_wins': team1_h2h_wins,
            'team2_h2h_wins': team2_h2h_wins,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Tab 2: Match Prediction
with tab2:
    st.header("🎯 Match Winner Prediction")

    col1, col2 = st.columns(2)

    with col1:
        pred_team1 = st.selectbox("Team 1", teams, key="pred_team1")
        venue = st.selectbox("Venue", sorted(matches['venue'].dropna().unique()), key="venue")

    with col2:
        pred_team2 = st.selectbox("Team 2", teams, key="pred_team2")
        toss_winner = st.selectbox("Toss Winner", [pred_team1, pred_team2], key="toss_winner")
        toss_decision = st.selectbox("Toss Decision", ["bat", "field"], key="toss_decision")

    if st.button("🔮 Predict Match Winner", type="primary"):
        if RandomForestClassifier and train_test_split:
            with st.spinner("Training model and making prediction..."):
                # Prepare data for training
                pred_data = matches[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner']].dropna()

                # Create features
                X = pd.get_dummies(pred_data[['team1', 'team2', 'venue', 'toss_winner', 'toss_decision']])
                y = pred_data['winner']

                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Train model
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)

                # Make prediction
                pred_features = pd.DataFrame({
                    'team1': [pred_team1],
                    'team2': [pred_team2],
                    'venue': [venue],
                    'toss_winner': [toss_winner],
                    'toss_decision': [toss_decision]
                })

                pred_X = pd.get_dummies(pred_features)

                # Align columns with training data
                for col in X_train.columns:
                    if col not in pred_X.columns:
                        pred_X[col] = 0
                pred_X = pred_X[X_train.columns]

                prediction = model.predict(pred_X)[0]
                probas = model.predict_proba(pred_X)[0]

                # Get team names and probabilities
                team_names = model.classes_
                team1_idx = list(team_names).index(pred_team1) if pred_team1 in team_names else -1
                team2_idx = list(team_names).index(pred_team2) if pred_team2 in team_names else -1

                team1_prob = probas[team1_idx] * 100 if team1_idx >= 0 else 0
                team2_prob = probas[team2_idx] * 100 if team2_idx >= 0 else 0

                # Display results
                st.success(f"🏆 Predicted Winner: **{prediction}**")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{pred_team1} Win Probability", f"{team1_prob:.1f}%")
                with col2:
                    st.metric(f"{pred_team2} Win Probability", f"{team2_prob:.1f}%")

                # Store prediction results for export
                st.session_state.prediction_results = {
                    'team1': pred_team1,
                    'team2': pred_team2,
                    'venue': venue,
                    'toss_winner': toss_winner,
                    'toss_decision': toss_decision,
                    'predicted_winner': prediction,
                    'team1_probability': team1_prob,
                    'team2_probability': team2_prob,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Accuracy on test set
                test_accuracy = accuracy_score(y_test, model.predict(X_test))
                st.info(f"🤖 Model Accuracy: {test_accuracy:.1f}% (based on test data)")

        else:
            st.error("⚠️ scikit-learn is required for predictions. Please install it with: `pip install scikit-learn`")

# Tab 3: Export Options
with tab3:
    st.header("📤 Export Your Analysis & Predictions")

    export_options = st.multiselect(
        "Select what to export:",
        ["Team Analysis Report", "Match Prediction Results", "Raw Matches Data", "Raw Deliveries Data"],
        default=["Team Analysis Report", "Match Prediction Results"]
    )

    if st.button("📄 Generate & Download Report", type="primary"):
        if not export_options:
            st.warning("Please select at least one export option.")
        else:
            # Create a comprehensive report
            report_data = {
                "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "IPL Data Summary": {
                    "Total Matches": len(matches),
                    "Total Deliveries": len(deliveries),
                    "Seasons Covered": len(matches['season'].unique()),
                    "Teams": len(teams)
                }
            }

            # Add team analysis if available
            if 'team_analysis' in st.session_state:
                report_data["Team Analysis"] = st.session_state.team_analysis

            # Add prediction results if available
            if 'prediction_results' in st.session_state:
                report_data["Match Prediction"] = st.session_state.prediction_results

            # Create downloadable files
            if "Team Analysis Report" in export_options and 'team_analysis' in st.session_state:
                analysis_df = pd.DataFrame([st.session_state.team_analysis])
                csv_analysis = analysis_df.to_csv(index=False)
                st.download_button(
                    "📊 Download Team Analysis CSV",
                    csv_analysis,
                    f"team_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

            if "Match Prediction Results" in export_options and 'prediction_results' in st.session_state:
                prediction_df = pd.DataFrame([st.session_state.prediction_results])
                csv_prediction = prediction_df.to_csv(index=False)
                st.download_button(
                    "🎯 Download Prediction Results CSV",
                    csv_prediction,
                    f"match_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

            if "Raw Matches Data" in export_options:
                csv_matches = matches.to_csv(index=False)
                st.download_button(
                    "📋 Download Matches Data CSV",
                    csv_matches,
                    f"matches_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

            if "Raw Deliveries Data" in export_options:
                csv_deliveries = deliveries.to_csv(index=False)
                st.download_button(
                    "📋 Download Deliveries Data CSV",
                    csv_deliveries,
                    f"deliveries_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

            # Generate comprehensive JSON report
            import json
            json_report = json.dumps(report_data, indent=2, default=str)
            st.download_button(
                "📄 Download Complete JSON Report",
                json_report,
                f"ipl_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )

            st.success("✅ Report generated successfully! Click the download buttons above.")

    # Preview current session data
    st.subheader("📋 Current Session Data Preview")

    if 'team_analysis' in st.session_state:
        st.write("**Team Analysis:**")
        st.json(st.session_state.team_analysis)

    if 'prediction_results' in st.session_state:
        st.write("**Prediction Results:**")
        st.json(st.session_state.prediction_results)

    if not ('team_analysis' in st.session_state or 'prediction_results' in st.session_state):
        st.info("💡 Perform team analysis and/or match prediction in the other tabs to generate exportable data.")
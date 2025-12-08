# =========================================================
# PAGE : ACCUEIL (Hero Section)
# =========================================================

if selected == "Accueil":

    st.title("Rent-A-Dream 🌍")
    st.markdown("### *« De la Fiat Panda au Dragon Rouge, nous louons vos rêves. »*")

    col_pres1, col_pres2 = st.columns([2, 1])

    with col_pres1:
        st.write("""
        Bienvenue dans la première agence de location multiverselle. 
        Notre mission est simple : fournir le moyen de transport adapté à **n'importe quelle situation**, 
        que ce soit pour aller chercher du pain, explorer les abysses ou conquérir un royaume voisin.
        
        **Nos engagements :**
        * 🛡️ **Sécurité** : Nos dragons sont vaccinés et nos freins vérifiés.
        * ⚡ **Rapidité** : Contrats signés en moins de 2 minutes.
        * 🤝 **Diversité** : Terre, Mer, Air... et au-delà.
        """)

    with col_pres2:
        logo_anim = st.session_state.lottie_cache.get("Voiture") or st.session_state.lottie_cache.get("default")
        if logo_anim:
            st_lottie(logo_anim, height=150, key="logo_anim")

    st.markdown("---")

    st.subheader("👥 L'Équipe de Direction")

    team1, team2, team3 = st.columns(3)

    with team1:
        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=Maxence", width=100)
        st.markdown("**Maxence PARISSE**")
        st.caption("PDG & Fondateur")

    with team3:
        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=Clémence", width=100)
        st.markdown("**Clémence CHARLES**")
        st.caption("Directeur Vétérinaire")

    with team2:
        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=Frédéric", width=100)
        st.markdown("**Frédéric ALLERON**")
        st.caption("Cheffe de la Sécurité & Responsable Flotte Marine")

    st.markdown("---")

    st.markdown("### 📈 Performance en temps réel")
    st.info("Voici les indicateurs en temps réel de votre agence.")

    total_revenue = sum(r.total_price for r in system.rentals)
    nb_maintenance = len([v for v in system.fleet if v.status == VehicleStatus.UNDER_MAINTENANCE])

    total_fleet = len(system.fleet)
    occupancy_rate = 0
    if total_fleet > 0:
        nb_rented = len([v for v in system.fleet if v.status == VehicleStatus.RENTED])
        occupancy_rate = nb_rented / total_fleet

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(label="💰 Chiffre d'Affaires", value=f"{total_revenue}€", delta="Cumul")
    
    with k2:
        st.metric(label="📊 Taux d'Occupation", value=f"{occupancy_rate*100:.1f}%", delta=f"{len(system.rentals)} contrats total")
        st.progress(occupancy_rate)

    with k3:
        delta_m = "- Danger" if nb_maintenance > 0 else "OK"
        color_m = "inverse" if nb_maintenance > 0 else "normal"
        st.metric(label="🔧 En Maintenance", value=str(nb_maintenance), delta=delta_m, delta_color=color_m)

        
    with k4:
        st.metric(label="👥 Base Clients", value=str(len(system.customers)), delta="Actifs")

    st.markdown("---")

    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        st.markdown("**Répartition de la Flotte**")
        if system.fleet:
            type_counts = {}
            for v in system.fleet:
                t_name = v.__class__.__name__
                type_counts[t_name] = type_counts.get(t_name, 0) + 1
            st.bar_chart(pd.DataFrame(list(type_counts.items()), columns=["Type", "Nombre"]).set_index("Type"), color="#457B9D")
        else:
            st.warning("Pas assez de données.")

    with c_chart2:
        st.markdown("**État de Santé du Parc**")
        if system.fleet:
            status_counts = {"Dispo": 0, "Loué": 0, "Maintenance": 0, "HS": 0}
            for v in system.fleet:
                if v.status == VehicleStatus.AVAILABLE: status_counts["Dispo"] += 1
                elif v.status == VehicleStatus.RENTED: status_counts["Loué"] += 1
                elif v.status == VehicleStatus.UNDER_MAINTENANCE: status_counts["Maintenance"] += 1
                else: status_counts["HS"] += 1
            st.bar_chart(pd.DataFrame(list(status_counts.items()), columns=["Statut", "Nombre"]).set_index("Statut"), color="#E63946")
        else:
            st.warning("Pas assez de données.")

# =========================================================
# PAGE : NOTRE FLOTTE (Catalogue)
# =========================================================

    
# =========================================================
# PAGE : RÉSERVATIONS (Anciennement Locations)
# =========================================================
elif selected == "Réservations":
    st.title("📝 Comptoir de Réservation")
    
    tab_new, tab_return = st.tabs(["Nouvelle Location", "Retour Véhicule"])
    
    with tab_new:
        if not system.customers:
            st.error("Veuillez d'abord créer un client dans l'onglet 'Clients'.")
        else:
            c1, c2 = st.columns(2)
            
            # Sélection Client
            client_dict = {f"{c.name}": c.id for c in system.customers}
            c_name = c1.selectbox("Client", list(client_dict.keys()))
            
            # Sélection Véhicule (Pré-sélection si clic depuis le catalogue)
            avail = [v for v in system.fleet if v.status == VehicleStatus.AVAILABLE]

            if avail:
                veh_dict = {}
                for v in avail:
                    nom_principal = getattr(v, 'brand', None) or getattr(v, 'name', 'Véhicule')
                    modele_secondaire = getattr(v, 'model', getattr(v, 'breed', ''))

                    label = f"#{v.id} - {nom_principal} {modele_secondaire} ({v.daily_rate}€/j)"
                    veh_dict[label] = v.id

                
                default_idx = 0
                if 'selected_vehicle_id' in st.session_state:
                    for idx, vid in enumerate(veh_dict.values()):
                        if vid == st.session_state.selected_vehicle_id:
                            default_idx = idx
                            break
                
                v_label = c2.selectbox("Véhicule", list(veh_dict.keys()), index=default_idx)
                
                days = st.slider("Durée (jours)", 1, 30, 3)
                
                if st.button("Valider le contrat", type="primary"):
                    cid = client_dict[c_name]
                    vid = veh_dict[v_label]
                    rental = system.create_rental(cid, vid, date.today(), date.today()+timedelta(days=days))
                    if rental:
                        save_data()
                        st.balloons()
                        st.success(f"Contrat signé ! Montant : {rental.total_price}€")
                        if 'selected_vehicle_id' in st.session_state: del st.session_state.selected_vehicle_id
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Aucun véhicule disponible.")

    with tab_return:
        actives = [r for r in system.rentals if r.is_active]
        if not actives:
            st.info("Aucun retour en attente.")
        else:
            r_opts = {}
            for r in actives:
                v = r.vehicle
                nom_v = getattr(v, 'brand', getattr(v, 'name', 'Inconnu'))
                r_opts[f"Contrat #{r.id} ({r.customer.name}) -> {nom_v}"] = r.id

            choice = st.selectbox("Sélectionner contrat", list(r_opts.keys()))
            if st.button("Confirmer le retour"):
                system.return_vehicle(r_opts[choice])
                save_data()
                st.success("Retour effectué.")
                time.sleep(1)
                st.rerun()

# =========================================================
# PAGE : GESTION CLIENTS
# =========================================================

elif selected == "Clients":
    st.title("👥 Base Clients & CRM")
    
    # Navigation interne par Onglets
    tab_list, tab_create, tab_edit, tab_history = st.tabs([
        "📇 Annuaire", "➕ Nouveau Client", "✏️ Modifier / Supprimer", "📜 Historique Locations"
    ])

    # -----------------------------------------------------
    # ONGLET 1 : ANNUAIRE (CARTES DE VISITE)
    # -----------------------------------------------------
    with tab_list:
        search_q = st.text_input("🔍 Rechercher un client (Nom, Permis, Email)...")
        
        # Filtrage
        filtered_clients = system.customers
        if search_q:
            q = search_q.lower()
            filtered_clients = [c for c in system.customers if q in c.name.lower() or q in c.driver_license.lower()]

        st.caption(f"{len(filtered_clients)} clients trouvés")
        st.markdown("---")

        if not filtered_clients:
            st.info("Aucun client trouvé. Utilisez l'onglet 'Nouveau Client'.")
        else:
            cols = st.columns(3)
            for i, c in enumerate(filtered_clients):
                with cols[i % 3]:
                    with st.container(border=True):
                        safe_name = c.name.replace(" ", "%20")
                        avatar_url = f"https://api.dicebear.com/7.x/initials/svg?seed={safe_name}&backgroundColor=E63946"

                        st.markdown(f"""
                            <img src="{avatar_url}" class="client-avatar">
                            <div class="client-info">
                                <h4 style="margin:0; padding-top:5px; color:inherit;">{c.name}</h4>
                                <small style="opacity:0.7">ID: {c.id}</small>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown("---")

                        st.markdown(f"🪪 **{c.driver_license}**")
                        st.markdown(f"📧 {c.email}")
                        st.markdown(f"📞 {c.phone}")

                        if st.button("Voir dossier", key=f"v_{c.id}", use_container_width=True):
                            st.toast(f"Dossier de {c.name} chargé.", icon="📂")

    # -----------------------------------------------------
    # ONGLET 2 : CRÉATION (FORMULAIRE PRO)
    # -----------------------------------------------------
    
    with tab_create:
        st.subheader("Enregistrer un nouveau client")
        with st.form("new_client_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nom Prénom *")
            p = c2.text_input("Numéro Permis *")
            e = c1.text_input("Email")
            t = c2.text_input("Téléphone")

            if st.form_submit_button("Valider l'inscription", type="primary"):
                if n and p:
                    nid = 1 if not system.customers else max(c.id for c in system.customers) + 1
                    system.add_customer(Customer(nid, n, p, e, t))
                    save_data()
                    st.success(f"Client **{n}** ajouté !")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Nom et Permis requis.")

    # -----------------------------------------------------
    # ONGLET 3 : MODIFICATION / SUPPRESSION
    # -----------------------------------------------------
    
    with tab_edit:
        st.subheader("Mise à jour dossier")
        if not system.customers:
            st.warning("Aucun client dans la base.")
        else:
            opts = {f"{c.name} ({c.driver_license})": c for c in system.customers}
            sel = st.selectbox("Rechercher client", list(opts.keys()))
            target = opts[sel]

            with st.form("edit_client"):
                c1, c2 = st.columns(2)
                en = c1.text_input("Nom", value=target.name)
                ep = c2.text_input("Permis", value=target.driver_license)
                ee = c1.text_input("Email", value=target.email)
                et = c2.text_input("Téléphone", value=target.phone)

                if st.form_submit_button("Sauvegarder modifications"):
                    target.name = en; target.driver_license = ep; target.email = ee; target.phone = et
                    save_data()
                    st.success("Modifications enregistrées.")
                    st.rerun()

            st.markdown("---")
            if st.button("🗑️ Supprimer ce client"):
                system.customers.remove(target)
                save_data()
                st.warning("Client supprimé.")
                st.rerun()

    # -----------------------------------------------------
    # ONGLET 4 : HISTORIQUE (NOUVEAU !)
    # -----------------------------------------------------
    with tab_history:
        st.subheader("Historique des locations")
        if not system.customers:
            st.info("Base vide.")
        else:
            opts = {f"{c.name}": c for c in system.customers}
            sel = st.selectbox("Voir historique de :", list(opts.keys()))
            client = opts[sel]
            
            # Filtre les locations du client
            history = [r for r in system.rentals if r.customer.id == client.id]
            
            if history:
                data_hist = []
                for r in history:
                    # Nom du véhicule intelligent
                    vname = getattr(r.vehicle, 'brand', getattr(r.vehicle, 'name', 'Véhicule'))
                    vmod = getattr(r.vehicle, 'model', getattr(r.vehicle, 'breed', ''))
                    
                    data_hist.append({
                        "Début": r.start_date,
                        "Fin": r.end_date,
                        "Véhicule": f"{vname} {vmod}",
                        "Montant": f"{r.total_price}€",
                        "Statut": "En cours" if r.is_active else "Terminé"
                    })
                st.dataframe(pd.DataFrame(data_hist), use_container_width=True)
            else:
                st.info(f"{client.name} n'a aucune location enregistrée.")

# =========================================================
# PAGE : ADMINISTRATION (GESTION DU PARC)
# =========================================================


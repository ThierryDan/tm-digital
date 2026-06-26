// == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
// FICHIER
DE
RÉFÉRENCE
COMPLET — C  # WINFORMS
// Tous
les
concepts
vus, avec
exemples
tirés
des
exercices
// == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

// == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
// 1.
PROPRIÉTÉS — get / set
// == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

/ *
*STRUCTURE
DE
BASE:
*
*private
TYPE
_champ; // champ
privé — stocke
la
vraie
valeur
*public
TYPE
Propriete // propriété
publique — porte
d
'accès
*{
    *get
{
return _champ;} // lire
la
valeur
* set
{_champ = value;} // écrire
la
valeur
*}
*
* "value"
est
un
mot
clé
automatique
dans
le
set —
*il
contient
ce
que
l
'utilisateur essaie d'
assigner.
* /

// ── EXEMPLE
1: Propriété
simple(get / set
basique) ──────────
// Tiré
de: GridItem(Lotto)


class Exemple_ProprieteSimple
    {
        private
    int
    _value;

    public
    int
    Value
    {
        get
    {
    return _value;} // lire
    set
    {_value = value;} // écrire
    }
    }

    // ── EXEMPLE
    2: Propriété
    avec
    VALIDATION ───────────────────
    // Tiré
    de: cours
    2 — classe
    Etudiant


class Exemple_ProprieteValidation
    {
        private
    int
    _age;

    public
    int
    Age
    {
        get
    {
    return _age;}
    set
    {


if (value >= 0) // on refuse les âges négatifs
_age = value;
}
}
}

// ── EXEMPLE
3: Propriété
avec
ACTION
AUTOMATIQUE ───────────
// Tiré
de: Score(GuessANumber) — met
à
jour
le
Label
auto


class Exemple_ProprieteAvecAction
    {
        private
    int
    _value;
    private
    System.Windows.Forms.Label
    _gui; // le
    label
    à
    mettre
    à
    jour

    public
    int
    Value
    {
        get
    {
    return _value;}
    set
    {


_value = value; // 1.
stocke
la
valeur
updateGui(); // 2.
action
automatique !
}
}

private
void
updateGui()
{
    _gui.Text = $"Score : {_value}"; // met
à
jour
le
label
}
}

// ── EXEMPLE
4: Propriété
avec
ACTION
sur
un
CONTRÔLE ───────
// Tiré
de: GridItem(Lotto) — change
la
couleur
auto


class Exemple_ProprieteControle: System.Windows.Forms.Label


{
    private
bool
_selected;

public
bool
Selected
{
    get
{
return _selected;}
set
{
_selected = value;
changeBackColor(); // change
la
couleur
automatiquement
}
}

private
void
changeBackColor()
{
if (_selected)
this.BackColor = System.Drawing.Color.Green;
else
this.BackColor = System.Drawing.SystemColors.Control;
}
}

// ── EXEMPLE
5: Propriété
LECTURE
SEULE ─────────────────────

class Exemple_ProprieteReadOnly
    {
        private
    double
    _ratio;

    public
    double
    Ratio
    {
        get
    {
    return _ratio;}
    private
    set
    {_ratio = value;} // seule
    la
    classe
    peut
    modifier
    }
    }

    // ── EXEMPLE
    6: Propriété
    AUTOMATIQUE(raccourci) ───────────
    // Quand
    pas
    besoin
    de
    logique
    dans
    get / set


class Exemple_ProprieteAuto
    {
        public
    string
    Nom
    {get;
    set;} // get
    et
    set
    publics
    public
    int
    Age
    {get;
    set;} // idem
    public
    double
    Prix
    {get;
    private
    set;} // set
    privé — lecture
    seule
    de
    l
    'extérieur
    }

    // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
    // 2.
    CONSTRUCTEURS
    // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

    / *
    *STRUCTURE
    DE
    BASE:
    *
    *public
    NomClasse(paramètres)
    *{
         * // initialisation
     *}
    *
    *Le
    constructeur
    est
    appelé
    automatiquement
    lors
    du
    "new".
    *Il
    sert
    à
    initialiser
    l
    'objet.
    * /

    // ── EXEMPLE
    1: Constructeur
    simple ─────────────────────────
    // Tiré
    de: Produit(PanierApp)

    class Exemple_ConstructeurSimple
        {
            public
        string
        Nom
        {get;
        set;}
        public
        double
        Prix
        {get;
        set;}

        public
        Exemple_ConstructeurSimple(string
        nom, double
        prix)
        {
            this.Nom = nom; // "this" = l
        'objet courant
        this.Prix = prix;
        }
        }

        // ── EXEMPLE
        2: Constructeur
        qui
        reçoit
        un
        contrôle
        WinForms ─
        // Tiré
        de: Score(GuessANumber)
        // On
        passe
        le
        Label
        depuis
        Form1
        pour
        que
        Score
        puisse
        le
        modifier

        class Exemple_ConstructeurAvecLabel
            {
                private
            int
            _value;
            private
            System.Windows.Forms.Label
            _gui;

            // On
            reçoit
            le
            Label
            depuis
            Form1
            public
            Exemple_ConstructeurAvecLabel(System.Windows.Forms.Label
            gui)
            {
                _gui = gui; // on
            stocke
            la
            référence
            au
            label
            }
            }
            // Utilisation
            dans
            Form1:
            // score = new
            Score(lblScore);  ← on
            passe
            lblScore
            en
            argument

            // ── EXEMPLE
            3: Constructeur
            avec
            initialisation
            d
            'un Timer ─
            // Tiré
            de: SelfDestroyingButton(ClickIt)

            class Exemple_ConstructeurAvecTimer:
                System.Windows.Forms.Button

            {
                private
            System.Windows.Forms.Timer
            _timer = new
            System.Windows.Forms.Timer();

            public
            Exemple_ConstructeurAvecTimer()
            {
            // Connecter
            l
            'événement Tick du timer
            _timer.Tick += timer_Tick;
            _timer.Enabled = true; // démarrer
            le
            timer
            }

            private
            void
            timer_Tick(object
            sender, System.EventArgs
            e)
            {
                _timer.Enabled = false;
            this.Parent?.Controls.Remove(this); // s
            'autodétruire
            }
            }

            // ── EXEMPLE
            4: Constructeur
            avec
            HÉRITAGE(base) ───────────
            // Tiré
            de: cours
            3 — héritage

            class Animal
                {
                    public
                string
                Nom
                {get;
                set;}
                public
                int
                Age
                {get;
                set;}

                public
                Animal(string
                nom, int
                age)
                {
                    this.Nom = nom;
                this.Age = age;
                }
                }

                class Chien:
                    Animal

                {
                    public
                string
                Race
                {get;
                set;}

                public
                Chien(string
                nom, int
                age, string
                race)
                : base(nom, age) // appelle
                le
                constructeur
                de
                Animal
                {
                    this.Race = race;
                }
                }

                // ── EXEMPLE
                5: Constructeur
                qui
                crée
                des
                contrôles
                internes ─
                // Tiré
                de: CarteEtudiant(CarteApp)
                // Crée
                des
                Labels
                à
                l
                'intérieur d'
                un
                Panel

                class Exemple_ConstructeurControlesInternes:
                    System.Windows.Forms.Panel

                {
                    private
                System.Windows.Forms.Label
                lblNom;
                private
                System.Windows.Forms.Label
                lblMoyenne;

                public
                Exemple_ConstructeurControlesInternes(string
                nom, double
                moyenne)
                {
                // Configurer
                le
                Panel
                lui - même(hérité)
                this.Width = 300;
                this.Height = 70;
                this.BackColor = moyenne >= 10
                ? System.Drawing.Color.LightGreen // ternaire !
                : System.Drawing.Color.LightCoral;

                // Créer
                les
                labels
                internes
                lblNom = new
                System.Windows.Forms.Label();
                lblNom.Text = $"Nom : {nom}";
                lblNom.Location = new
                System.Drawing.Point(10, 10);
                lblNom.AutoSize = true;

                lblMoyenne = new
                System.Windows.Forms.Label();
                lblMoyenne.Text = $"Moyenne : {moyenne}/20";
                lblMoyenne.Location = new
                System.Drawing.Point(10, 35);
                lblMoyenne.AutoSize = true;

                // Ajouter
                les
                labels
                AU
                panel
                this.Controls.Add(lblNom);
                this.Controls.Add(lblMoyenne);
                }
                }

                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                // 3.
                CLASSES
                PERSONNALISÉES
                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                / *
                *TYPES
                DE
                CLASSES
                VUES:
                *1.
                Classe
                métier
                pure(données
                sans
                affichage)
                *2.
                Classe
                graphique(hérite
                d
                'un contrôle WinForms)
                * 3.
                Classe
                de
                gestion(gère
                une
                liste + événements)
                * /

                // ── EXEMPLE
                1: Classe
                métier
                pure ──────────────────────────
                // Tiré
                de: Produit(PanierApp)

                class Produit
                    {
                        public
                    string
                    Nom
                    {get;
                    set;}
                    public
                    double
                    Prix
                    {get;
                    set;}
                    public
                    int
                    Stock
                    {get;
                    set;}

                    public
                    Produit(string
                    nom, double
                    prix, int
                    stock)
                    {
                        this.Nom = nom;
                    this.Prix = prix;
                    this.Stock = stock;
                    }

                    public
                    bool
                    EstDisponible()
                    {

                return Stock > 0;
                }

                // ToString — appelé
                automatiquement
                par
                ListBox
                public
                override
                string
                ToString()
                {
                return $"{Nom} - {Prix}€ - stock : {Stock}";
                }
                }

                // ── EXEMPLE
                2: Classe
                graphique
                héritant
                de
                Label ──────────
                // Tiré
                de: GridItem(Lotto)

                class GridItem:
                    System.Windows.Forms.Label

                {
                    private
                int
                _value;
                private
                bool
                _selected;

                public
                int
                Value
                {
                    get
                {
                return _value;}
                set
                {_value = value;}
                }

                public
                bool
                Selected
                {
                    get
                {
                return _selected;}
                set
                {
                _selected = value;
                changeBackColor(); // action
                auto
                au
                changement
                }
                }

                private
                void
                changeBackColor()
                {
                if (_selected)
                this.BackColor = System.Drawing.Color.Green;
                else
                this.BackColor = System.Drawing.SystemColors.Control;
                }
                }

                // ── EXEMPLE
                3: Classe
                graphique
                héritant
                de
                Button ─────────
                // Tiré
                de: SelfDestroyingButton(ClickIt)

                class SelfDestroyingButton:
                    System.Windows.Forms.Button

                {
                    private
                int
                _value;
                private
                System.Windows.Forms.Timer
                _timer = new
                System.Windows.Forms.Timer();

                public
                int
                Value
                {
                    get
                {
                return _value;}
                set
                {_value = value;
                setColor();} // couleur
                auto !
                }

                public
                int
                TimeOut
                {
                    get
                {
                return _timer.Interval;}
                set
                {_timer.Interval = value;}
                }

                public
                SelfDestroyingButton()
                {
                    _timer.Tick += timer_Tick;
                _timer.Enabled = true;
                }

                private
                void
                timer_Tick(object
                sender, System.EventArgs
                e)
                {
                    _timer.Enabled = false;
                this.Parent?.Controls.Remove(this); // s
                'autodétruit !
                }

                private
                void
                setColor()
                {
                    switch(_value)
                {
                case
                1: this.BackColor = System.Drawing.Color.White;
                break;
                case
                2: this.BackColor = System.Drawing.Color.Red;
                break;
                case
                3: this.BackColor = System.Drawing.Color.Purple;
                break;
                default: this.BackColor = System.Drawing.Color.Black;
                break;
                }
                }
                }

                // ── EXEMPLE
                4: Classe
                graphique
                héritant
                de
                Panel ──────────
                // Tiré
                de: CarteEtudiant(CarteApp)
                et
                WarningLight

                class WarningLight:
                    System.Windows.Forms.Panel

                {
                    private
                System.Drawing.Color
                _color;
                private
                bool
                _blink;
                private
                int
                _blinkDelay = 500;
                private
                System.Windows.Forms.Timer
                _blinkTimer = new
                System.Windows.Forms.Timer();

                public
                System.Drawing.Color
                Color
                {
                    get
                {
                return _color;}
                set
                {_color = value;
                this.BackColor = value;} // change
                couleur
                auto
                }

                public
                bool
                Blink
                {
                    get
                {
                return _blink;}
                set
                {
                _blink = value;
                _blinkTimer.Enabled = value; // démarre / arrête
                le
                clignotement
                }
                }

                public
                int
                Blink_Delay
                {
                    get
                {
                return _blinkDelay;}
                set
                {_blinkDelay = value;
                _blinkTimer.Interval = value;}
                }

                public
                WarningLight()
                {
                    _blinkTimer.Tick += blinkTimer_Tick;
                }

                private
                void
                blinkTimer_Tick(object
                sender, System.EventArgs
                e)
                {
                // Alterne
                entre
                visible
                et
                invisible
                this.Visible = !this.Visible;
                }
                }

                // ── EXEMPLE
                5: Classe
                de
                gestion
                avec
                List < T > ──────────────
                // Tiré
                de: Catalogue(PanierApp)

                class Catalogue
                    {
                        private
                    System.Collections.Generic.List < Produit > _produits
                    = new
                    System.Collections.Generic.List < Produit > ();

                    // Événement
                    personnalisé
                    public
                    delegate
                    void
                    ProduitAjouteHandler(object
                    sender, Produit
                    e);
                    public
                    event
                    ProduitAjouteHandler
                    ProduitAjoute;

                    public
                    void
                    AjouterProduit(string
                    nom, double
                    prix, int
                    stock)
                    {
                        Produit
                    p = new
                    Produit(nom, prix, stock);
                    _produits.Add(p);
                    ProduitAjoute?.Invoke(this, p); // déclenche
                    l
                    'événement
                    }

                    public
                    void
                    Supprimer(int
                    index)
                    {
                        _produits.RemoveAt(index);
                    }

                    public
                    int
                    GetCount()
                    {

                return _produits.Count;
                }
                }

                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                // 4.
                ÉVÉNEMENTS
                PERSONNALISÉS
                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                / *
                * STRUCTURE:
                *1.
                delegate  → définit
                la
                FORME
                de
                la
                méthode
                qui
                réagira
                * 2.
                event     → le
                SIGNAL
                basé
                sur
                ce
                delegate
                * 3.
                Invoke()  → DÉCLENCHE
                l
                'événement
                * 4. +=        → S
                'ABONNER à l'
                événement
                * /

                // ── EXEMPLE
                1: Événement
                sans
                données(EventArgs.Empty) ────
                // Tiré
                de: Catalogue(PanierApp)
                version
                simple

                class Exemple_EvenementSimple
                    {
                    // 1.
                    Delegate — forme
                    de
                    la
                    méthode
                    réceptrice
                    public
                    delegate
                    void
                    ChangementHandler(object
                    sender, System.EventArgs
                    e);

                    // 2.
                    Event — le
                    signal
                    public
                    event
                    ChangementHandler
                    Changement;

                    public
                    void
                    FaireQuelqueChose()
                    {
                    // ...
                    logique...

                    // 3.
                    Déclencher — le ? évite
                    un
                    crash
                    si
                    personne
                    n
                    'écoute
                    Changement?.Invoke(this, System.EventArgs.Empty);
                    }
                    }
                    // Dans
                    Form1:
                    // monObjet.Changement += monObjet_Changement; // 4.
                    S
                    'abonner
                    // private
                    void
                    monObjet_Changement(object
                    sender, EventArgs
                    e) {...}

                    // ── EXEMPLE
                    2: Événement
                    AVEC
                    données
                    personnalisées ────────
                    // Tiré
                    de: PanierApp — transmet
                    le
                    Produit
                    ajouté

                    class ProduitEventArgs:
                        System.EventArgs

                    {
                        public
                    string
                    NomProduit
                    {get;
                    set;}
                    public
                    double
                    Prix
                    {get;
                    set;}

                    public
                    ProduitEventArgs(string
                    nom, double
                    prix)
                    {
                        this.NomProduit = nom;
                    this.Prix = prix;
                    }
                    }

                    class Exemple_EvenementAvecDonnees
                        {
                            public
                        delegate
                        void
                        ProduitAjouteHandler(object
                        sender, ProduitEventArgs
                        e);
                        public
                        event
                        ProduitAjouteHandler
                        ProduitAjoute;

                        public
                        void
                        AjouterProduit(string
                        nom, double
                        prix)
                        {
                            ProduitEventArgs
                        args = new
                        ProduitEventArgs(nom, prix);
                        ProduitAjoute?.Invoke(this, args); // transmet
                        les
                        données !
                        }
                        }
                        // Dans
                        Form1:
                        // private
                        void
                        catalogue_ProduitAjoute(object
                        sender, ProduitEventArgs
                        e)
                        // {
                           // lstProduits.Items.Add($"{e.NomProduit} - {e.Prix}€");
                        //}

                        // ── EXEMPLE
                        3: Événement
                        qui
                        transmet
                        l
                        'OBJET directement ──
                        // Tiré
                        de: Catalogue
                        version
                        avancée

                        class Exemple_EvenementObjet
                            {
                                public
                            delegate
                            void
                            ProduitAjouteHandler(object
                            sender, Produit
                            e);
                            public
                            event
                            ProduitAjouteHandler
                            ProduitAjoute;

                            public
                            void
                            AjouterProduit(string
                            nom, double
                            prix, int
                            stock)
                            {
                                Produit
                            p = new
                            Produit(nom, prix, stock);
                            ProduitAjoute?.Invoke(this, p); // transmet
                            directement
                            l
                            'objet
                            }
                            }

                            // ── EXEMPLE
                            4: Deux
                            événements
                            dans
                            la
                            même
                            classe ─────────
                            // Tiré
                            de: Buffer(ControleLigneProduction)

                            class Exemple_DeuxEvenements
                                {
                                    public
                                delegate
                                void
                                ValueChangedHandler(object
                                sender, System.EventArgs
                                e);
                                public
                                delegate
                                void
                                StatusChangedHandler(object
                                sender, System.EventArgs
                                e);

                                public
                                event
                                ValueChangedHandler
                                ValueChanged;
                                public
                                event
                                StatusChangedHandler
                                FillingStatusChanged;

                                private
                                double
                                _value;
                                private
                                string
                                _status = "Ok";

                                public
                                double
                                Value
                                {
                                    get
                                {
                                return _value;}
                                set
                                {

                            _value = value;
                            ValueChanged?.Invoke(this, System.EventArgs.Empty); // événement
                            1
                            checkStatus();
                            }
                            }

                            private
                            void
                            checkStatus()
                            {
                                string
                            newStatus = _value > 70 ? "Critical": "Ok";
                            if (newStatus != _status)
                            {
                            _status = newStatus;
                            FillingStatusChanged?.Invoke(this, System.EventArgs.Empty); // événement
                            2
                            }
                            }
                            }

                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                            // 5.
                            HÉRITAGE
                            DE
                            CONTRÔLES
                            WINFORMS
                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                            / *
                            * RÈGLE:

                            class MaClasse:
                                ControleWinForms

                            *Tu
                            récupères
                            TOUT
                            ce
                            que
                            le
                            contrôle
                            possède
                            *et
                            tu
                            ajoutes
                            tes
                            propres
                            propriétés / méthodes
                            par
                            dessus.
                            *
                            *Contrôles
                            courants
                            à
                            hériter:
                            *- Label   → texte
                            affiché, léger
                            *- Button  → cliquable, interactif
                            *- Panel   → conteneur, peut
                            contenir
                            d
                            'autres contrôles
                            * /

                            // ── EXEMPLE
                            1: Hériter
                            de
                            Label ────────────────────────────
                            // Tiré
                            de: GridItem(Lotto)
                            // Utile
                            quand
                            tu
                            veux
                            un
                            label
                            avec
                            des
                            données
                            supplémentaires

                            class MonLabel:
                                System.Windows.Forms.Label

                            {
                                public
                            int
                            Id
                            {get;
                            set;} // donnée
                            supplémentaire
                            public
                            bool
                            Actif
                            {get;
                            set;} // état
                            supplémentaire
                            }

                            // ── EXEMPLE
                            2: Hériter
                            de
                            Button ───────────────────────────
                            // Tiré
                            de: SelfDestroyingButton(ClickIt)
                            // Utile
                            quand
                            tu
                            veux
                            un
                            bouton
                            avec
                            comportement
                            spécial

                            class MonButton:
                                System.Windows.Forms.Button

                            {
                                public
                            string
                            Categorie
                            {get;
                            set;}

                            public
                            MonButton(string
                            texte, string
                            categorie)
                            {
                                this.Text = texte; // propriété
                            héritée
                            de
                            Button
                            this.Categorie = categorie; // ta
                            propriété
                            personnalisée
                            this.BackColor = System.Drawing.Color.LightBlue;
                            this.Width = 150;
                            this.Height = 40;
                            }
                            }

                            // ── EXEMPLE
                            3: Hériter
                            de
                            Panel ────────────────────────────
                            // Tiré
                            de: CarteEtudiant(CarteApp)
                            et
                            WarningLight
                            // Utile
                            quand
                            tu
                            veux
                            un
                            conteneur
                            avec
                            comportement
                            spécial

                            class MonPanel:
                                System.Windows.Forms.Panel

                            {
                                private
                            System.Windows.Forms.Label
                            lblInfo;

                            public
                            MonPanel(string
                            info)
                            {
                            // Configurer
                            le
                            panel(hérité)
                            this.Width = 200;
                            this.Height = 60;
                            this.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;

                            // Créer
                            des
                            contrôles
                            internes
                            lblInfo = new
                            System.Windows.Forms.Label();
                            lblInfo.Text = info;
                            lblInfo.Location = new
                            System.Drawing.Point(10, 10);
                            lblInfo.AutoSize = true;

                            // Ajouter
                            au
                            panel
                            this.Controls.Add(lblInfo);
                            }
                            }

                            // ── EXEMPLE
                            4: Cast
                            pour
                            récupérer
                            le
                            vrai
                            type ────────────
                            // Tiré
                            de: GridItem_Click(Lotto)
                            et
                            newButtonClick(ClickIt)
                            / *
                            private
                            void
                            monControle_Click(object
                            sender, EventArgs
                            e)
                            {
                            // sender
                            est
                            de
                            type
                            "object" — trop
                            générique
                            // On
                            caste
                            pour
                            accéder
                            à
                            nos
                            propriétés
                            personnalisées

                            MonButton
                            btn = (MonButton)
                            sender; // cast !
                            Console.WriteLine(btn.Categorie); // maintenant
                            accessible
                            }
                            * /

                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                            // 6.
                            ENUM
                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                            / *
                            *Un
                            enum = liste
                            de
                            valeurs
                            NOMMÉES
                            prédéfinies
                            *Utile
                            pour
                            représenter
                            des
                            états, niveaux, catégories...
                            * /

                            // ── EXEMPLE
                            1: Enum
                            simple ─────────────────────────────────
                            // Tiré
                            de: Buffer(ControleLigneProduction)
                            enum
                            Status
                            {Ok, Warning, Critical}

                            // Utilisation:
                            // Status
                            monStatus = Status.Ok;
                            // if (monStatus == Status.Warning) {...}

                            // ── EXEMPLE
                            2: Enum
                            dans
                            un
                            switch ─────────────────────────
                            // Tiré
                            de: ControlWindow(ControleLigneProduction)
                            / *
                            switch(buffer.FillingStatus)
                            {
                                case
                            Status.Ok: \
                                panelBuffer.BackColor = Color.Green;
                            break;
                            case
                            Status.Warning:
                            panelBuffer.BackColor = Color.Yellow;
                            break;
                            case
                            Status.Critical:
                            panelBuffer.BackColor = Color.Red;
                            break;
                            }
                            * /

                            // ── EXEMPLE
                            3: Enum
                            dans
                            une
                            propriété ─────────────────────

                            class Exemple_EnumPropriete
                                {
                                    private
                                Status
                                _fillingStatus = Status.Ok;

                                public
                                Status
                                FillingStatus
                                {
                                    get
                                {
                                return _fillingStatus;}
                                private
                                set
                                {

                            if (_fillingStatus != value) // seulement si le statut change !
                            {
                                _fillingStatus = value;
                            // déclencher
                            un
                            événement...
                            }
                            }
                            }
                            }

                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                            // 7.
                            TIMER
                            // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                            / *
                            * Le
                            Timer
                            déclenche
                            un
                            événement
                            toutes
                            les
                            X
                            millisecondes.
                            * Deux
                            façons
                            de
                            l
                            'utiliser :
                            * 1.
                            Glissé
                            depuis
                            la
                            boîte
                            à
                            outils → dans
                            Form1
                            * 2.
                            Créé
                            dans
                            le
                            code → dans
                            une
                            classe
                            personnalisée
                            * /

                            // ── EXEMPLE
                            1: Timer
                            dans
                            Form1(boîte
                            à
                            outils) ───────────
                            // Tiré
                            de: GuessANumber, ClickIt
                                              / *
                                              // Dans
                            le
                            Designer: glisser
                            Timer, Interval = 1000, Enabled = false

                            private
                            void
                            timer1_Tick(object
                            sender, EventArgs
                            e)
                            {
                                time - -;
                            lblTimer.Text = $"Temps restant : {time}";

                            if (time <= 0)
                            {
                            timer1.Enabled = false; // arrêter le timer
                            // fin du jeu...
                            }
                            }
                            * /

                            // ── EXEMPLE 2: Timer
                            créé
                            dans
                            une
                            classe ──────────────────
                            // Tiré
                            de: SelfDestroyingButton(ClickIt)

                            class Exemple_TimerDansClasse
                                {
                                    private
                                System.Windows.Forms.Timer
                                _timer = new
                                System.Windows.Forms.Timer();

                                public
                                int
                                Interval
                                {
                                    get
                                {
                                return _timer.Interval;}
                                set
                                {_timer.Interval = value;}
                                }

                                public
                                Exemple_TimerDansClasse()
                                {
                                    _timer.Tick += timer_Tick; // connecter
                                l
                                'événement
                                _timer.Interval = 1000; // 1
                                seconde
                                par
                                défaut
                                _timer.Enabled = true; // démarrer
                                }

                                private
                                void
                                timer_Tick(object
                                sender, System.EventArgs
                                e)
                                {
                                    _timer.Enabled = false; // arrêter
                                                               // faire
                                quelque
                                chose...
                                }
                                }

                                // ── EXEMPLE
                                3: Timer
                                pour
                                mise
                                à
                                jour
                                régulière ────────────
                                // Tiré
                                de: Buffer(ControleLigneProduction) — toutes
                                les
                                100
                                ms

                            class Exemple_TimerMiseAJour
                                {
                                    private
                                System.Windows.Forms.Timer
                                _updateTimer = new
                                System.Windows.Forms.Timer();
                                private
                                double
                                _value = 0;
                                private
                                double
                                _inputFlow = 0;
                                private
                                double
                                _outputFlow = 0;

                                public
                                Exemple_TimerMiseAJour()
                                {
                                    _updateTimer.Interval = 100; // toutes
                                les
                                100
                                ms
                                _updateTimer.Tick += update_Tick;
                                _updateTimer.Enabled = true;
                                }

                                private
                                void
                                update_Tick(object
                                sender, System.EventArgs
                                e)
                                {
                                // Calcul: valeur
                                change
                                selon
                                flux
                                entrée / sortie
                                double
                                diff = _inputFlow - _outputFlow;
                                _value += diff * (_updateTimer.Interval / 1000.0);
                                // déclencher
                                événements
                                si
                                nécessaire...
                                }
                                }

                                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                                // 8.
                                LISTES
                                ET
                                GESTION
                                D
                                'OBJETS
                                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                                / *
                                *List < T > — liste
                                dynamique
                                qui
                                grandit / rétrécit
                                *Toujours
                                déclarer
                                au
                                NIVEAU
                                DE
                                LA
                                CLASSE
                                dans
                                Form1
                                *pour
                                être
                                accessible
                                dans
                                toutes
                                les
                                méthodes
                                * /

                                // ── EXEMPLE
                                1: List < T > dans
                                Form1 ──────────────────────────
                                // Tiré
                                de: GestionEtudiants
                                / *
                                public
                                partial

                                class Form1:
                                    Form

                                {
                                // Au
                                niveau
                                de
                                la
                                classe — accessible
                                partout !
                                private
                                List < Etudiant > etudiants = new
                                List < Etudiant > ();

                                private
                                void
                                btnAjouter_Click(object
                                sender, EventArgs
                                e)
                                {
                                    Etudiant
                                e2 = new
                                Etudiant(txtNom.Text, 14.5);
                                etudiants.Add(e2); // ajouter
                                lstEtudiants.Items.Add(e2); // afficher
                                lblInfo.Text = $"{etudiants.Count} étudiants";
                                }

                                private
                                void
                                btnSupprimer_Click(object
                                sender, EventArgs
                                e)
                                {
                                    int
                                index = lstEtudiants.SelectedIndex;
                                if (index == -1)
                                    return; // rien
                                sélectionné

                                etudiants.RemoveAt(index); // supprimer
                                de
                                la
                                liste
                                lstEtudiants.Items.RemoveAt(index); // supprimer
                                de
                                l
                                'affichage
                                lblInfo.Text = $"{etudiants.Count} étudiants";
                                }
                                }
                                * /

                                // ── EXEMPLE
                                2: Tableau
                                fixe(quand
                                taille
                                connue) ──────────
                                // Tiré
                                de: Lotto — toujours
                                42
                                cases
                                / *
                                GridItem[]
                                loteryGrid = new
                                GridItem[42]; // tableau
                                de
                                42
                                éléments

                                for (int i = 0; i < 42; i++)
                                {
                                    loteryGrid[i] = new GridItem();
                                //...
                                }
                                * /

                                // ── EXEMPLE 3: Création
                                dynamique
                                dans
                                une
                                boucle ──────────
                                // Tiré
                                de: Lotto — crée
                                42
                                GridItem
                                en
                                code
                                / *
                                for (int i = 0; i < 42; i++)
                                {
                                    GridItem btn = new GridItem();
                                btn.Text = (i + 1).ToString();
                                btn.Value = i + 1;
                                btn.AutoSize = true;
                                btn.Click += GridItem_Click;

                                // Calcul position en grille avec %et /
                                int x = i % 4; // colonne (modulo)
                                int y = i / 4; // ligne   (division entière)
                                btn.Location = new System.Drawing.Point(20 + x * 38, 20 + y * 38);

                                panelLottoGrid.Controls.Add(btn); // ajouter au panel
                                }
                                * /

                                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
                                // 9. PATTERNS COURANTS À RETENIR
                                // == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

                                / *
                                * ── PATTERN 1: btnAjouter_Click ────────────────────────────
                                *
                                * 1.
                                Vérifier
                                les
                                champs
                                vides
                                * 2.
                                Convertir
                                avec
                                TryParse
                                si
                                nécessaire
                                * 3.
                                Créer
                                l
                                'objet
                                * 4.
                                Ajouter
                                à
                                la
                                liste
                                ET
                                à
                                l
                                'affichage
                                * 5.
                                Mettre
                                à
                                jour
                                le
                                compteur
                                * 6.
                                Vider
                                les
                                champs
                                *
                                *
                                * ── PATTERN
                                2: btnSupprimer_Click ──────────────────────────
                                *
                                * 1.
                                Récupérer
                                SelectedIndex
                                * 2.
                                Vérifier
                                si == -1(rien
                                sélectionné)
                                *3.
                                RemoveAt(index)
                                sur
                                la
                                liste
                                * 4.
                                RemoveAt(index)
                                sur
                                la
                                ListBox
                                * 5.
                                Mettre
                                à
                                jour
                                le
                                compteur
                                *
                                *
                                * ── PATTERN
                                3: TryParse ────────────────────────────────────
                                *
                                * double
                                prix;
                                * if (!double.TryParse(txtPrix.Text, out prix))
                                *{
                                    *lblInfo.Text = "Nombre invalide !";
                                * return;
                                *}
                                * // ici
                                prix
                                contient
                                la
                                valeur
                                convertie
                                *
                                *
                                * ── PATTERN
                                4: Cast
                                sender ─────────────────────────────────
                                *
                                * private
                                void
                                monControle_Click(object
                                sender, EventArgs
                                e)
                                *{
                                *MonType
                                obj = (MonType)
                                sender; // cast
                                obligatoire
                                *obj.MaPropriete... // accès
                                aux
                                propriétés
                                *}
                                *
                                *
                                * ── PATTERN
                                5: S
                                'autodétruire ──────────────────────────────
                                *
                                * this.Parent?.Controls.Remove(this);
                                * // this.Parent = le
                                formulaire
                                ou
                                panel
                                contenant
                                ce
                                contrôle
                                * // ? = si
                                Parent
                                est
                                null, ne
                                rien
                                faire(sécurité)
                                *
                                *
                                * ── PATTERN
                                6: DialogResult ────────────────────────────────
                                *
                                * DialogResult
                                res = MessageBox.Show(
                                *"Rejouer ?",
                                *"Fin de partie",
                                *MessageBoxButtons.YesNo
                                * );
                                * if (res == DialogResult.Yes)
                                {reset();}
                                * else {this.Close();}
                                *
                                *
                                * ── PATTERN
                                7: Abonnement
                                à
                                un
                                événement ───────────────────
                                *
                                * // Dans
                                le
                                constructeur
                                de
                                Form1:
                                *monObjet.MonEvenement += monObjet_MonEvenement;
                                *
                                * // La
                                méthode
                                réceptrice:
                                *private
                                void
                                monObjet_MonEvenement(object
                                sender, EventArgs
                                e)
                                *{
                                * // réagir
                                à
                                l
                                'événement
                                *}
                                * /
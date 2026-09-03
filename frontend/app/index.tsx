import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useMemo, useState } from "react";
import { Alert, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

const C = { forest: "#183D2C", emerald: "#286445", olive: "#89A95A", gold: "#C39A45", cream: "#F7F5EC", card: "#FFFFFF", ink: "#193329", muted: "#758078", line: "#E8E7DE" };

function Macro({ label, value, target, color }: { label: string; value: number; target: number; color: string }) {
  return <View style={s.macro}><View style={s.macroTop}><Text style={s.macroLabel}>{label}</Text><Text style={s.macroValue}>{value}<Text style={s.macroTarget}>/{target} g</Text></Text></View><View style={s.track}><View style={[s.fill, { width: `${Math.min(value / target, 1) * 100}%`, backgroundColor: color }]} /></View></View>;
}

function Action({ icon, title, subtitle }: { icon: keyof typeof Ionicons.glyphMap; title: string; subtitle: string }) {
  return <Pressable style={({ pressed }) => [s.action, pressed && s.pressed]} onPress={() => soon(title)}><View style={s.actionIcon}><Ionicons name={icon} size={20} color={C.emerald} /></View><View style={s.actionCopy}><Text style={s.actionTitle}>{title}</Text><Text style={s.actionSub}>{subtitle}</Text></View><Ionicons name="chevron-forward" size={18} color="#A9AFA9" /></Pressable>;
}

const soon = (title: string) => Alert.alert(title, "Cet accès sera relié à son écran lors de la prochaine étape.");

export default function HomeScreen() {
  const [generated, setGenerated] = useState(false);
  const today = useMemo(() => new Intl.DateTimeFormat("fr-FR", { weekday: "long", day: "numeric", month: "long" }).format(new Date()), []);
  const generate = () => { setGenerated(true); Alert.alert("Préparation de ta semaine", "Le questionnaire de personnalisation va maintenant pouvoir s’ouvrir."); };

  return <SafeAreaView style={s.safe}>
    <View style={s.screen}>
      <ScrollView contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        <View style={s.header}>
          <View style={s.brand}><View style={s.brandMark}><Ionicons name="leaf" size={20} color={C.gold} /></View><View><Text style={s.brandName}>KETO-ESSENCIEL</Text><Text style={s.tagline}>SIMPLE · NATUREL · ESSENTIEL</Text></View></View>
          <Pressable style={s.bell} onPress={() => soon("Notifications")}><Ionicons name="notifications-outline" size={22} color={C.forest} /><View style={s.dot} /></Pressable>
        </View>
        <View style={s.welcome}>
          <View><Text style={s.eyebrow}>{today.toUpperCase()}</Text><Text style={s.greeting}>Bonjour Patrice</Text><Text style={s.greetingSub}>Ton équilibre keto, simplement.</Text></View>
          <View style={s.badge}><Ionicons name="sparkles" size={13} color={C.gold} /><Text style={s.badgeText}>PREMIUM</Text></View>
        </View>

        <LinearGradient colors={["#173F2C", "#2B6A48"]} style={s.weekCard}>
          <View style={s.orb1} /><View style={s.orb2} />
          <View style={s.weekCopy}><Text style={s.weekKicker}>{generated ? "TA SEMAINE EST PRÊTE" : "MON PROGRAMME PERSONNALISÉ"}</Text><Text style={s.weekTitle}>{generated ? "Découvrir mes 7 jours" : "Générer ma semaine"}</Text><Text style={s.weekText}>{generated ? "Tes menus, recettes et courses sont réunis au même endroit." : "Des menus keto adaptés à ton objectif, tes goûts et ton rythme."}</Text>
            <Pressable style={({ pressed }) => [s.weekButton, pressed && s.pressed]} onPress={generate}><Text style={s.weekButtonText}>{generated ? "Voir ma semaine" : "Commencer"}</Text><Ionicons name="arrow-forward" size={17} color={C.forest} /></Pressable>
          </View>
          <View style={s.weekIcon}><Ionicons name="calendar" size={40} color="#F5E8BE" /><Text style={s.weekNumber}>7</Text></View>
        </LinearGradient>

        <Header title="Aujourd’hui" subtitle="Ton équilibre nutritionnel" link="Voir le détail" />
        <View style={s.macrosCard}>
          <View style={s.calorieRow}><View style={s.gauge}><View style={s.gaugeInner}><Text style={s.calorie}>1 240</Text><Text style={s.kcal}>kcal</Text></View></View><View style={s.calorieCopy}><Text style={s.calorieTitle}>640 kcal restantes</Text><Text style={s.calorieSub}>66 % de ton objectif quotidien</Text></View></View>
          <View style={s.divider} /><Macro label="Glucides nets" value={18} target={25} color={C.gold} /><Macro label="Protéines" value={79} target={113} color="#5B8D70" /><Macro label="Lipides" value={91} target={135} color={C.olive} />
        </View>

        <Header title="Au menu" subtitle="Ton prochain repas" link="12:30" pill />
        <Pressable style={({ pressed }) => [s.mealCard, pressed && s.pressed]} onPress={() => soon("Menu du jour")}>
          <LinearGradient colors={["#E3EAD3", "#F7F5EC"]} style={s.mealVisual}><View style={s.plate}><Ionicons name="restaurant" size={30} color={C.emerald} /></View></LinearGradient>
          <View style={s.mealCopy}><Text style={s.mealKicker}>DÉJEUNER · 25 MIN</Text><Text style={s.mealTitle}>Poulet crémeux aux épinards</Text><Text style={s.mealMeta}>6 g glucides nets · 42 g protéines</Text><View style={s.mealLinkRow}><Text style={s.mealLink}>Voir la recette</Text><Ionicons name="arrow-forward" size={15} color={C.emerald} /></View></View>
        </Pressable>

        <Text style={[s.sectionTitle, { marginBottom: 12 }]}>Mes essentiels</Text>
        <View style={s.actionsCard}><Action icon="checkmark-circle-outline" title="Mon check-in du jour" subtitle="4 objectifs sur 6 complétés" /><View style={s.actionDivider} /><Action icon="trending-down-outline" title="Ma progression" subtitle="– 3,8 kg depuis le début" /><View style={s.actionDivider} /><Action icon="bag-handle-outline" title="Ma liste de courses" subtitle="12 articles restant à cocher" /></View>
        <LinearGradient colors={["#F1E9D5", "#F7F3E8"]} style={s.tip}><View style={s.tipIcon}><Ionicons name="leaf-outline" size={22} color={C.gold} /></View><View style={s.tipCopy}><Text style={s.tipKicker}>LE CONSEIL DU NATUROPATHE</Text><Text style={s.tipText}>Prépare ton eau dès le matin : ce geste simple aide à garder une hydratation régulière.</Text></View></LinearGradient>
      </ScrollView>
      <View style={s.nav}><Nav icon="home" label="Accueil" active /><Nav icon="restaurant-outline" label="Menus" /><Pressable style={s.add} onPress={() => soon("Espace rapide")}><Ionicons name="add" size={30} color="white" /></Pressable><Nav icon="stats-chart-outline" label="Suivi" /><Nav icon="person-outline" label="Profil" /></View>
    </View>
  </SafeAreaView>;
}

function Header({ title, subtitle, link, pill }: { title: string; subtitle: string; link: string; pill?: boolean }) {
  return <View style={s.sectionHeader}><View><Text style={s.sectionTitle}>{title}</Text><Text style={s.sectionSub}>{subtitle}</Text></View><Pressable onPress={() => soon(link)}><Text style={pill ? s.pill : s.textLink}>{link}</Text></Pressable></View>;
}
function Nav({ icon, label, active }: { icon: keyof typeof Ionicons.glyphMap; label: string; active?: boolean }) {
  return <Pressable style={s.navItem} onPress={() => !active && soon(label)}><Ionicons name={icon} size={22} color={active ? C.emerald : C.muted} /><Text style={active ? s.navActive : s.navLabel}>{label}</Text></Pressable>;
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: C.cream }, screen: { flex: 1, backgroundColor: C.cream }, content: { paddingHorizontal: 18, paddingTop: 12, paddingBottom: 124 },
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }, brand: { flexDirection: "row", alignItems: "center", gap: 10 }, brandMark: { width: 37, height: 37, borderRadius: 19, backgroundColor: C.forest, alignItems: "center", justifyContent: "center" }, brandName: { color: C.forest, fontSize: 15, fontWeight: "800", letterSpacing: 1.1 }, tagline: { marginTop: 2, color: C.gold, fontSize: 7.5, fontWeight: "700", letterSpacing: 1.35 },
  bell: { width: 42, height: 42, borderRadius: 21, backgroundColor: C.card, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: C.line }, dot: { position: "absolute", top: 8, right: 9, width: 7, height: 7, borderRadius: 4, backgroundColor: C.gold, borderWidth: 1.5, borderColor: C.card },
  welcome: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 18 }, eyebrow: { color: C.gold, fontSize: 9, fontWeight: "800", letterSpacing: 1.2, marginBottom: 5 }, greeting: { color: C.ink, fontSize: 27, lineHeight: 32, fontWeight: "700" }, greetingSub: { color: C.muted, fontSize: 13, marginTop: 3 }, badge: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 9, paddingVertical: 6, backgroundColor: "#EFE7D4", borderRadius: 20 }, badgeText: { color: "#8A692A", fontSize: 9, fontWeight: "800", letterSpacing: .8 },
  weekCard: { minHeight: 205, borderRadius: 27, padding: 22, overflow: "hidden", flexDirection: "row", marginBottom: 27, shadowColor: "#173D2B", shadowOpacity: .19, shadowRadius: 18, shadowOffset: { width: 0, height: 10 }, elevation: 6 }, weekCopy: { flex: 1, zIndex: 2 }, weekKicker: { color: "#DCCB91", fontSize: 9, fontWeight: "800", letterSpacing: 1.25, marginBottom: 9 }, weekTitle: { color: "white", fontSize: 25, lineHeight: 29, fontWeight: "700", maxWidth: 230 }, weekText: { color: "#D6E2DA", fontSize: 12.5, lineHeight: 18, marginTop: 8, maxWidth: 235 }, weekButton: { marginTop: 18, height: 40, paddingHorizontal: 16, borderRadius: 20, backgroundColor: "#F5E8BE", alignSelf: "flex-start", flexDirection: "row", gap: 9, alignItems: "center" }, weekButtonText: { color: C.forest, fontSize: 12, fontWeight: "800" }, weekIcon: { width: 72, height: 72, borderRadius: 36, borderWidth: 1, borderColor: "rgba(245,232,190,.35)", backgroundColor: "rgba(255,255,255,.09)", alignItems: "center", justifyContent: "center", alignSelf: "center", marginLeft: 8 }, weekNumber: { position: "absolute", top: 28, color: C.forest, fontWeight: "900", fontSize: 12 }, orb1: { position: "absolute", width: 180, height: 180, borderRadius: 90, right: -75, top: -90, borderWidth: 1, borderColor: "rgba(255,255,255,.09)" }, orb2: { position: "absolute", width: 110, height: 110, borderRadius: 55, right: -35, bottom: -55, backgroundColor: "rgba(137,169,90,.12)" },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 12 }, sectionTitle: { color: C.ink, fontSize: 20, lineHeight: 24, fontWeight: "700" }, sectionSub: { color: C.muted, fontSize: 12, marginTop: 2 }, textLink: { color: C.emerald, fontSize: 11.5, fontWeight: "700" }, pill: { color: C.emerald, fontSize: 11, fontWeight: "700", backgroundColor: "#E7F0E9", paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12 },
  macrosCard: { backgroundColor: C.card, borderRadius: 24, padding: 18, marginBottom: 27, borderWidth: 1, borderColor: "#EEEDE6" }, calorieRow: { flexDirection: "row", alignItems: "center" }, gauge: { width: 76, height: 76, borderRadius: 38, borderWidth: 8, borderColor: "#DBE5CE", borderTopColor: C.olive, borderRightColor: C.olive, alignItems: "center", justifyContent: "center", transform: [{ rotate: "-15deg" }] }, gaugeInner: { transform: [{ rotate: "15deg" }], alignItems: "center" }, calorie: { color: C.ink, fontSize: 15, fontWeight: "800" }, kcal: { color: C.muted, fontSize: 9 }, calorieCopy: { flex: 1, paddingLeft: 17 }, calorieTitle: { color: C.ink, fontSize: 15, fontWeight: "700" }, calorieSub: { color: C.muted, fontSize: 11.5, marginTop: 5 }, divider: { height: 1, backgroundColor: C.line, marginVertical: 17 },
  macro: { marginBottom: 13 }, macroTop: { flexDirection: "row", justifyContent: "space-between", marginBottom: 7 }, macroLabel: { color: "#59675F", fontSize: 11.5, fontWeight: "600" }, macroValue: { color: C.ink, fontSize: 11.5, fontWeight: "800" }, macroTarget: { color: C.muted, fontWeight: "500" }, track: { height: 5, borderRadius: 4, backgroundColor: "#ECEDE8", overflow: "hidden" }, fill: { height: "100%", borderRadius: 4 },
  mealCard: { minHeight: 144, backgroundColor: C.card, borderRadius: 22, overflow: "hidden", flexDirection: "row", borderWidth: 1, borderColor: "#EEEDE6", marginBottom: 27 }, mealVisual: { width: "34%", alignItems: "center", justifyContent: "center" }, plate: { width: 72, height: 72, borderRadius: 36, backgroundColor: "rgba(255,255,255,.8)", borderWidth: 5, borderColor: "white", alignItems: "center", justifyContent: "center" }, mealCopy: { flex: 1, padding: 16, justifyContent: "center" }, mealKicker: { color: C.gold, fontSize: 8.5, fontWeight: "800", letterSpacing: .9 }, mealTitle: { color: C.ink, fontSize: 16, lineHeight: 20, fontWeight: "700", marginTop: 6 }, mealMeta: { color: C.muted, fontSize: 10.5, marginTop: 6 }, mealLinkRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: 10 }, mealLink: { color: C.emerald, fontSize: 11.5, fontWeight: "700" },
  actionsCard: { backgroundColor: C.card, borderRadius: 24, paddingHorizontal: 15, marginBottom: 22, borderWidth: 1, borderColor: "#EEEDE6" }, action: { minHeight: 78, flexDirection: "row", alignItems: "center" }, actionIcon: { width: 42, height: 42, borderRadius: 14, backgroundColor: "#EDF2E8", alignItems: "center", justifyContent: "center" }, actionCopy: { flex: 1, paddingHorizontal: 12 }, actionTitle: { color: C.ink, fontSize: 14, fontWeight: "700" }, actionSub: { color: C.muted, fontSize: 10.5, marginTop: 4 }, actionDivider: { height: 1, backgroundColor: C.line, marginLeft: 54 },
  tip: { borderRadius: 22, padding: 17, flexDirection: "row", alignItems: "flex-start" }, tipIcon: { width: 42, height: 42, borderRadius: 21, backgroundColor: "rgba(255,255,255,.68)", alignItems: "center", justifyContent: "center" }, tipCopy: { flex: 1, paddingLeft: 13 }, tipKicker: { color: "#997329", fontSize: 8.5, fontWeight: "800", letterSpacing: .9, marginBottom: 6 }, tipText: { color: "#5C523D", fontSize: 12, lineHeight: 18 },
  nav: { position: "absolute", left: 12, right: 12, bottom: 10, height: 72, borderRadius: 25, backgroundColor: "rgba(255,255,255,.98)", flexDirection: "row", alignItems: "center", justifyContent: "space-around", borderWidth: 1, borderColor: C.line, shadowColor: C.forest, shadowOpacity: .12, shadowRadius: 18, shadowOffset: { width: 0, height: 7 }, elevation: 8 }, navItem: { width: 58, alignItems: "center", justifyContent: "center", gap: 3 }, navLabel: { color: C.muted, fontSize: 9.5, fontWeight: "600" }, navActive: { color: C.emerald, fontSize: 9.5, fontWeight: "700" }, add: { width: 54, height: 54, borderRadius: 27, backgroundColor: C.forest, alignItems: "center", justifyContent: "center", marginTop: -34, borderWidth: 4, borderColor: C.cream, shadowColor: C.forest, shadowOpacity: .25, shadowRadius: 9, elevation: 6 }, pressed: { opacity: .78, transform: [{ scale: .99 }] },
});

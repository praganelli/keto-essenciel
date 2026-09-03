import { Ionicons } from "@expo/vector-icons";
import { BlurView } from "expo-blur";
import { useState } from "react";
import {
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const REFERENCE_WIDTH = 853;

const MOCKUP_SECTIONS = [
  { source: require("@/assets/images/home-approved-1.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-2.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-3.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-4.jpg"), height: 240 },
];

const NAV_ITEMS = [
  { id: "home", label: "Accueil", icon: "home-outline", activeIcon: "home" },
  { id: "menus", label: "Menus", icon: "restaurant-outline", activeIcon: "restaurant" },
  { id: "tracking", label: "Suivi", icon: "analytics-outline", activeIcon: "analytics" },
  { id: "profile", label: "Profil", icon: "person-outline", activeIcon: "person" },
] as const;

export default function HomeScreen() {
  const { width } = useWindowDimensions();
  const pageWidth = Math.min(width, 520);
  const [activeTab, setActiveTab] = useState("home");

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator
        alwaysBounceVertical
        directionalLockEnabled
        contentInset={{ bottom: 112 }}
        scrollIndicatorInsets={{ bottom: 112 }}
      >
        {MOCKUP_SECTIONS.map((section, index) => (
          <Image
            key={index}
            source={section.source}
            resizeMode="stretch"
            style={{
              width: pageWidth,
              height: pageWidth * (section.height / REFERENCE_WIDTH),
            }}
            accessibilityLabel={index === 0 ? "Page d’accueil Keto-Essenciel" : undefined}
          />
        ))}
      </ScrollView>

      <View style={styles.navPosition} pointerEvents="box-none">
        <BlurView intensity={76} tint="systemUltraThinMaterialLight" style={styles.navGlass}>
          <View style={styles.navHighlight} />
          {NAV_ITEMS.slice(0, 2).map((item) => (
            <NavItem key={item.id} item={item} active={activeTab === item.id} onPress={setActiveTab} />
          ))}

          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Ouvrir les actions rapides"
            onPress={() => setActiveTab("quick")}
            style={({ pressed }) => [styles.addButton, pressed && styles.pressed]}
          >
            <View style={styles.addShine} />
            <Ionicons name="add" size={35} color="#FFFFFF" />
          </Pressable>

          {NAV_ITEMS.slice(2).map((item) => (
            <NavItem key={item.id} item={item} active={activeTab === item.id} onPress={setActiveTab} />
          ))}
        </BlurView>
      </View>
    </SafeAreaView>
  );
}

type NavItemProps = {
  item: (typeof NAV_ITEMS)[number];
  active: boolean;
  onPress: (id: string) => void;
};

function NavItem({ item, active, onPress }: NavItemProps) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected: active }}
      onPress={() => onPress(item.id)}
      style={({ pressed }) => [styles.navItem, pressed && styles.pressed]}
    >
      {active && <View style={styles.activePill} />}
      <Ionicons
        name={active ? item.activeIcon : item.icon}
        size={22}
        color={active ? "#0C513B" : "#626762"}
      />
      <Text style={[styles.navLabel, active && styles.navLabelActive]}>{item.label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#FBFAF6" },
  scroll: { flex: 1 },
  scrollContent: { alignItems: "center", flexGrow: 1, paddingBottom: 112 },
  navPosition: {
    position: "absolute",
    left: 16,
    right: 16,
    bottom: 12,
    alignItems: "center",
  },
  navGlass: {
    width: "100%",
    maxWidth: 488,
    height: 76,
    borderRadius: 32,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.82)",
    backgroundColor: "rgba(250,252,248,0.42)",
    overflow: "visible",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingHorizontal: 8,
    shadowColor: "#173B2D",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 22,
    elevation: 14,
  },
  navHighlight: {
    position: "absolute",
    top: 1,
    left: 24,
    right: 24,
    height: 1,
    backgroundColor: "rgba(255,255,255,0.95)",
  },
  navItem: {
    width: 57,
    height: 62,
    alignItems: "center",
    justifyContent: "center",
    gap: 3,
  },
  activePill: {
    position: "absolute",
    width: 52,
    height: 52,
    borderRadius: 20,
    backgroundColor: "rgba(143,190,87,0.17)",
  },
  navLabel: { fontSize: 10.5, color: "#626762", fontWeight: "500" },
  navLabelActive: { color: "#0C513B", fontWeight: "700" },
  addButton: {
    width: 62,
    height: 62,
    borderRadius: 31,
    marginTop: -22,
    backgroundColor: "rgba(77,164,53,0.92)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.9)",
    shadowColor: "#3C7E2C",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.32,
    shadowRadius: 12,
    elevation: 10,
    overflow: "hidden",
  },
  addShine: {
    position: "absolute",
    top: 4,
    left: 12,
    width: 30,
    height: 13,
    borderRadius: 12,
    backgroundColor: "rgba(255,255,255,0.24)",
    transform: [{ rotate: "-12deg" }],
  },
  pressed: { opacity: 0.72, transform: [{ scale: 0.96 }] },
});

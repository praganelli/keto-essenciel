import { useState } from "react";
import {
  Alert,
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
const REFERENCE_HEIGHT = 1844;

const MOCKUP_SECTIONS = [
  { source: require("@/assets/images/home-approved-1.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-2.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-3.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-4.jpg"), height: 344 },
];

type Hotspot = {
  id: string;
  label: string;
  left: number;
  top: number;
  width: number;
  height: number;
};

const HOTSPOTS: Hotspot[] = [
  { id: "notifications", label: "Notifications", left: 86, top: 2, width: 11, height: 7 },
  { id: "programme", label: "Voir mon programme", left: 27, top: 42, width: 45, height: 7 },
  { id: "checkin", label: "Check-in", left: 13, top: 49, width: 24, height: 8 },
  { id: "menu", label: "Menu", left: 38, top: 49, width: 24, height: 8 },
  { id: "courses", label: "Courses", left: 63, top: 49, width: 24, height: 8 },
  { id: "generate", label: "Générer ma semaine", left: 61, top: 57, width: 31, height: 7 },
  { id: "week", label: "Mon menu de la semaine", left: 75, top: 72, width: 20, height: 5 },
  { id: "home", label: "Accueil", left: 10, top: 93, width: 16, height: 7 },
  { id: "menus", label: "Menus", left: 27, top: 93, width: 18, height: 7 },
  { id: "quick", label: "Actions rapides", left: 43, top: 92, width: 16, height: 8 },
  { id: "tracking", label: "Suivi", left: 61, top: 93, width: 17, height: 7 },
  { id: "profile", label: "Profil", left: 79, top: 93, width: 16, height: 7 },
];

export default function HomeScreen() {
  const { width } = useWindowDimensions();
  const [active, setActive] = useState<string | null>(null);
  const pageWidth = Math.min(width, 520);
  const pageHeight = pageWidth * (REFERENCE_HEIGHT / REFERENCE_WIDTH);

  const open = (item: Hotspot) => {
    setActive(item.id);
    Alert.alert(item.label, "Cet écran sera connecté dans la prochaine étape du développement.");
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        bounces={false}
      >
        <View style={[styles.mockup, { width: pageWidth, height: pageHeight }]}>
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
          {HOTSPOTS.map((item) => (
            <Pressable
              key={item.id}
              accessibilityRole="button"
              accessibilityLabel={item.label}
              onPress={() => open(item)}
              style={({ pressed }) => [
                styles.hotspot,
                {
                  left: `${item.left}%`,
                  top: `${item.top}%`,
                  width: `${item.width}%`,
                  height: `${item.height}%`,
                },
                pressed && styles.hotspotPressed,
              ]}
            >
              {active === item.id && <Text style={styles.srOnly}>{item.label}</Text>}
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#FBFAF6" },
  scroll: { flex: 1, backgroundColor: "#FBFAF6" },
  scrollContent: { alignItems: "center" },
  mockup: { position: "relative", backgroundColor: "#FBFAF6", overflow: "hidden" },
  hotspot: { position: "absolute", borderRadius: 18 },
  hotspotPressed: { backgroundColor: "rgba(135, 170, 51, 0.14)" },
  srOnly: { width: 1, height: 1, opacity: 0 },
});

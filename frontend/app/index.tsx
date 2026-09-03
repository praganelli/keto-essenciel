import { Image, ScrollView, StyleSheet, useWindowDimensions } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const REFERENCE_WIDTH = 853;

const MOCKUP_SECTIONS = [
  { source: require("@/assets/images/home-approved-1.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-2.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-3.jpg"), height: 500 },
  { source: require("@/assets/images/home-approved-4.jpg"), height: 344 },
];

export default function HomeScreen() {
  const { width } = useWindowDimensions();
  const pageWidth = Math.min(width, 520);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator
        alwaysBounceVertical
        directionalLockEnabled
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#FBFAF6" },
  scroll: { flex: 1 },
  scrollContent: { alignItems: "center", flexGrow: 1 },
});

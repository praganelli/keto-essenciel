import { useState } from "react";
import { View, StyleSheet, ActivityIndicator, Platform } from "react-native";
import { WebView } from "react-native-webview";

const APP_URL = `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/app`;

export default function Index() {
  const [loading, setLoading] = useState(true);

  // On web, react-native-webview renders an iframe.
  if (Platform.OS === "web") {
    return (
      <View style={styles.container} testID="keto-app-container">
        {/* eslint-disable-next-line react/no-unknown-property */}
        <iframe
          src={APP_URL}
          title="Keto Premium"
          style={{ border: "none", width: "100%", height: "100%" }}
        />
      </View>
    );
  }

  return (
    <View style={styles.container} testID="keto-app-container">
      <WebView
        testID="keto-app-webview"
        source={{ uri: APP_URL }}
        style={styles.webview}
        originWhitelist={["*"]}
        javaScriptEnabled
        domStorageEnabled
        onLoadEnd={() => setLoading(false)}
        startInLoadingState
      />
      {loading && (
        <View style={styles.loader} testID="keto-app-loader">
          <ActivityIndicator size="large" color="#c49030" />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0c0c0c" },
  webview: { flex: 1, backgroundColor: "#0c0c0c" },
  loader: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0c0c0c",
  },
});

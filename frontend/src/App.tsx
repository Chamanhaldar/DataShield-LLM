import { type ChangeEvent, useEffect } from "react";
import {
  Box,
  Container,
  Flex,
  HStack,
  IconButton,
  Input,
  Spacer,
  Text,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import { MoonIcon, SunIcon } from "@chakra-ui/icons";
import { QueryClient, QueryClientProvider } from "react-query";

import { configureTokenProvider } from "./api/client";
import { InferenceConsole } from "./features/inference/components/InferenceConsole";
import { useAuthStore, type AuthState } from "./store/auth";

const queryClient = new QueryClient();

const Header = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const bg = useColorModeValue("gray.50", "gray.900");
  const token = useAuthStore((state: AuthState) => state.token);
  const setToken = useAuthStore((state: AuthState) => state.setToken);

  return (
    <Box borderBottomWidth="1px" bg={bg} py={3}>
      <Container maxW="6xl">
        <Flex align="center" gap={4}>
          <Text fontSize="lg" fontWeight="bold">
            Sentinel LLM Guard
          </Text>
          <Spacer />
          <HStack spacing={2}>
            <Input
              placeholder="Paste JWT token"
              value={token ?? ""}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setToken(event.target.value || null)}
              maxW="320px"
            />
            <IconButton
              aria-label="Toggle color mode"
              icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
            />
          </HStack>
        </Flex>
      </Container>
    </Box>
  );
};

const AppShell = () => {
  const token = useAuthStore((state: AuthState) => state.token);

  useEffect(() => {
    configureTokenProvider(() => token);
  }, [token]);

  return (
    <Box minH="100vh" bg={useColorModeValue("gray.100", "gray.800")} py={10}>
      <Container maxW="6xl">
        <InferenceConsole />
      </Container>
    </Box>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <Header />
    <AppShell />
  </QueryClientProvider>
);

export default App;

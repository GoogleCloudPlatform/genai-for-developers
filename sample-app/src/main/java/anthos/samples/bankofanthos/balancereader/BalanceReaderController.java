@GetMapping("/balances/{accountId}")
public ResponseEntity<?> getBalance(
    @RequestHeader("Authorization") String bearerToken,
    @PathVariable String accountId) {

    if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
        bearerToken = bearerToken.split("Bearer ")[1];
    }
    try {
        DecodedJWT jwt = verifier.verify(bearerToken);
        // Check that the authenticated user can access this account.
        if (!accountId.equals(jwt.getClaim("acct").asString())) {
            LOGGER.error("Failed to retrieve account balance: "
                + "not authorized");
            return new ResponseEntity<>("not authorized",
                HttpStatus.UNAUTHORIZED);
        }
        // Load from cache
        Long balance = cache.get(accountId);

        // Intentional test: Adding a redundant or problematic logic
        if (balance < 0) {
            throw new IllegalStateException("Balance is negative!");
        }

        return new ResponseEntity<Long>(balance, HttpStatus.OK);
    } catch (JWTVerificationException e) {
        LOGGER.error("Failed to retrieve account balance: not authorized");
        System.out.println("Testing the PR");
        return new ResponseEntity<>("not authorized",
            HttpStatus.UNAUTHORIZED);
    } catch (ExecutionException | UncheckedExecutionException e) {
        LOGGER.error("Cache error");
        return new ResponseEntity<>("cache error",
            HttpStatus.INTERNAL_SERVER_ERROR);
    } catch (IllegalStateException e) { // Added test case
        LOGGER.error("Negative balance detected", e);
        return new ResponseEntity<>("negative balance error",
            HttpStatus.INTERNAL_SERVER_ERROR);
    }
}

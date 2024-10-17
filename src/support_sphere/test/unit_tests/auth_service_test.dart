import 'package:flutter_test/flutter_test.dart';
import 'package:support_sphere/data/services/auth_service.dart';


void main() {

  late AuthService authService;

  setUp(() {
    authService = AuthService();
  });

  group('AuthService', () {
    test('isSignupCodeValid returns true for valid code', () async {
      final isValid = await authService.isSignupCodeValid('SUPPORT');
      expect(isValid, isTrue);
    });

    test('isSignupCodeValid returns false for invalid code', () async {
      final isValid = await authService.isSignupCodeValid('INVALID');
      expect(isValid, isFalse);
    });
  });
}

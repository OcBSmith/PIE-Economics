using Test
using MacroAIComp

@testset "ISLM Tests" begin
    @testset "Steady State Default Calibration" begin
        params = default_calibration(ISLMParams)
        ss = steady_state(params)

        @test ss["Y"] ≈ 2000.0 atol=1e-6
        @test ss["P"] ≈ 81.0 atol=1e-6
        @test ss["i"] ≈ 2.0 atol=1e-6
        @test ss["Yd"] ≈ 2000.0 atol=1e-6
        @test ss["dP"] ≈ 0.0 atol=1e-6
        @test ss["dY"] ≈ 0.0 atol=1e-6
    end

    @testset "System Dynamics at Steady State" begin
        params = default_calibration(ISLMParams)
        ss = steady_state(params)
        state = [ss["Y"], ss["P"]]

        derivatives = system_dynamics(state, params, 0.0)

        @test derivatives[1] ≈ 0.0 atol=1e-6  # dY/dt
        @test derivatives[2] ≈ 0.0 atol=1e-6  # dP/dt
    end

    @testset "Monetary Shock" begin
        params = default_calibration(ISLMParams)
        # Shock: money supply increases from 100 to 101.
        # Since Julia structs are immutable, we reconstruct it.
        params_shocked = ISLMParams(
            params.theta,
            params.psi,
            params.beta1,
            params.mi,
            params.ni,
            params.beta0,
            101.0,
            params.ypot0
        )
        ss_new = steady_state(params_shocked)

        @test ss_new["Y"] ≈ 2000.0 atol=1e-6
        @test ss_new["i"] ≈ 2.0 atol=1e-6
        @test ss_new["P"] ≈ 82.0 atol=1e-6
    end
end
